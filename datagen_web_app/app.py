from flask import Flask, render_template, request, send_file, abort, make_response
import os
import scipy.io as sio
from logic.load_matrix import load_matrix
from logic.optimize import optimize_matrix
from logic.wavelet import scale_sparse_matrix_wavelet
from logic.nearest import scale_sparse_matrix_nearest
from logic.bilinear import scale_sparse_matrix_bilinear
from logic.lanczos import scale_sparse_matrix_lanczos
from logic.gaussian import scale_sparse_matrix_gaussian
from logic.image import scale_sparse_matrix_image
from logic.visualize_matrix import visualize_matrices
from PIL import Image
from scipy.sparse import csr_matrix

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded-matrices'
GENERATED_FOLDER = 'generated-matrices'
OPTIMIZED_FOLDER = 'optimized-matrices'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)
os.makedirs(OPTIMIZED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Clear previous visualization if it exists
    visual_path = os.path.join("static", "last_visualization.png")
    if os.path.exists(visual_path):
        os.remove(visual_path)

    return render_template('index.html')

@app.route('/visualization')
def serve_visualization():
    visual_path = "static/last_visualization.png"
    if os.path.exists(visual_path):
        response = make_response(send_file(visual_path, mimetype='image/png'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        return '', 404

@app.route('/generate', methods=['POST'])
def generate():
    # 1. Handle uploaded file
    uploaded_file = request.files.get('matrix_upload')
    if not uploaded_file or not uploaded_file.filename.endswith('.mtx'):
        return "No valid matrix file uploaded.", 400

    matrix_filename = uploaded_file.filename
    upload_path = os.path.join(UPLOAD_FOLDER, matrix_filename)
    uploaded_file.save(upload_path)

    # 2. Extract form values
    algorithm = request.form.get('algorithm')
    rows = int(request.form.get('rows', 0))
    cols = int(request.form.get('cols', 0))
    match_nnz = 'match_nnz' in request.form
    optimize = 'optimize' in request.form

    kernel_size = 3
    if algorithm == "Lanczos Resampling":
        raw_kernel = request.form.get('kernel_size', '')
        if raw_kernel.strip().isdigit():
            kernel_size = int(raw_kernel)

    image_resampling = request.form.get('image_resampling_method', 'Image.BOX')

    # 3. Load the matrix
    matrix = load_matrix(upload_path)
    if matrix is None:
        return "Failed to load uploaded matrix.", 500

    # 4. Prepare output path
    output_filename = f"{os.path.splitext(matrix_filename)[0]}_{algorithm.replace(' ', '_')}.mtx"
    output_path = os.path.join(OPTIMIZED_FOLDER if optimize else GENERATED_FOLDER, output_filename)

    # 5. Dispatch based on algorithm
    result = csr_matrix((0, 0))  # safe init
    if algorithm == "Wavelet Transformation":
        result = scale_sparse_matrix_wavelet(matrix, rows, cols)
    elif algorithm == "Nearest-neighbor Interpolation":
        result = scale_sparse_matrix_nearest(matrix, rows, output_path, match_nnz)
    elif algorithm == "Bi-linear Interpolation":
        result = scale_sparse_matrix_bilinear(matrix, rows, output_path, match_nnz)
    elif algorithm == "Lanczos Resampling":
        result = scale_sparse_matrix_lanczos(matrix, rows, output_path, match_nnz, kernel_size)
    elif algorithm == "Gaussian Pyramids":
        result = scale_sparse_matrix_gaussian(matrix, rows, output_path, match_nnz)
    elif algorithm == "Image-based Scaling":
        resize_method = getattr(Image, image_resampling.split('.')[-1])
        result = scale_sparse_matrix_image(matrix, rows, output_path, resize_method)
    else:
        return "Unsupported algorithm selected.", 400

    # 6. Optional optimization
    if optimize:
        result = optimize_matrix(result)

    # 7. Save result
    sio.mmwrite(output_path, result)

    # 8. Save visualization
    visual_path = os.path.join("static", "last_visualization.png")
    visualize_matrices(matrix, result, save_path=visual_path)

    # 9. Render the page again and pass image path
    return render_template("index.html", image_path=visual_path)

if __name__ == '__main__':
    app.run(debug=True)
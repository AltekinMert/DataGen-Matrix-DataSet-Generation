import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from gui import (
    create_main_window,
    create_directory_frame,
    create_file_listbox,
    create_dimension_input_frame,
    create_buttons,
    create_metadata_frame,
    create_matrix_image_frame
)
import scipy.io
import os
import numpy as np
import scipy.sparse as sp
import traceback
from scipy.sparse.linalg import svds
from matrix_features import compute_features, compute_average_features
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.sparse import csr_matrix

# Global variables
loaded_matrices = []
computed_features_list = []

def select_directory():
    # Function to select a directory and list .mtx files
    directory = filedialog.askdirectory()
    if directory:
        dir_label.config(text=directory)
        list_mtx_files(directory)

def list_mtx_files(directory):
    file_listbox.delete(0, tk.END)
    files = [f for f in os.listdir(directory) if f.endswith('.mtx')]
    if files:
        for file in files:
            file_listbox.insert(tk.END, file)
    else:
        messagebox.showwarning("No Files", "No .mtx files found in the selected directory.")

def load_selected_files():
    # Load the selected .mtx files and display their properties
    selected_indices = file_listbox.curselection()
    directory = dir_label.cget("text")

    if selected_indices:
        matrices = []
        metadata_list = []
        features_list = []
        for idx in selected_indices:
            selected_file = file_listbox.get(idx)
            file_path = os.path.join(directory, selected_file)
            try:
                metadata = extract_metadata(file_path)
                metadata_list.append(metadata)

                matrix = scipy.io.mmread(file_path).tocsr()
                matrices.append(matrix)

                features = compute_features(matrix)
                features_list.append(features)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the .mtx file: {e}")
                return

        global loaded_matrices, computed_features_list
        loaded_matrices = matrices
        computed_features_list = features_list

        if metadata_list:
            update_metadata_labels(metadata_list[0])

        inspect_button.config(state=tk.NORMAL)
        generate_button.config(state=tk.NORMAL)

def extract_metadata(file_path):
    metadata = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('%'):
                if ':' in line:
                    key_value = line.strip('% \n').split(':', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        metadata[key.strip()] = value.strip()
            else:
                break
    return metadata

def update_metadata_labels(metadata):
    name_label.config(text=f"Name: {metadata.get('name', '-')}")
    id_label.config(text=f"ID: {metadata.get('id', '-')}")
    date_label.config(text=f"Date: {metadata.get('date', '-')}")
    author_label.config(text=f"Author: {metadata.get('author', '-')}")
    ed_label.config(text=f"Ed: {metadata.get('ed', '-')}")
    kind_label.config(text=f"Kind: {metadata.get('kind', '-')}")

def draw_matrix_image(matrix, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()
    dpi = 100  
    fig_width = frame_width / dpi
    fig_height = frame_height / dpi

    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_subplot(111)
    ax.spy(matrix, markersize=1)
    ax.set_title('Matrix Visualization')
    ax.axis('off')  

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
    frame.grid_propagate(False)

def show_features_window():
    features_window = tk.Toplevel(root)
    features_window.title("Matrix Features")
    features_window.geometry("800x600")

    features_frame = tk.Frame(features_window)
    features_frame.pack(expand=True, fill=tk.BOTH)

    tree = ttk.Treeview(features_frame, columns=('Feature', 'Value'), show='headings')
    tree.heading('Feature', text='Feature')
    tree.heading('Value', text='Value')
    tree.column('Feature', width=300)
    tree.column('Value', width=250)

    average_features = compute_average_features(computed_features_list)
    for key, value in average_features.items():
        if isinstance(value, float):
            value = f"{value:.4f}"
        elif isinstance(value, bool):
            value = 'Yes' if value else 'No'
        else:
            value = str(value)
        tree.insert('', tk.END, values=(key, value))

    scrollbar = ttk.Scrollbar(features_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    if loaded_matrices:
        matrix_image_frame = tk.Frame(features_frame, bg="white", relief="sunken", width=400, height=400)
        matrix_image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        draw_matrix_image(loaded_matrices[0], matrix_image_frame)



def generate_new_matrix():
    global loaded_matrices, computed_features_list
    try:
        if len(loaded_matrices) == 0:
            messagebox.showerror("No Matrices Loaded", "Please select matrices to generate a new matrix.")
            return

        user_rows = rows_entry.get()
        user_cols = cols_entry.get()
        if user_rows and user_cols:
            try:
                desired_rows = int(user_rows)
                desired_cols = int(user_cols)
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid integers for dimensions.")
                return
        else:
            messagebox.showerror("Input Error", "Please specify desired dimensions for extrapolation.")
            return

        scaled_matrices = []
        for matrix in loaded_matrices:
            scaled_matrix = scale_matrix(matrix, desired_rows, desired_cols)
            scaled_matrices.append(scaled_matrix)

        sparsity_mask = (scaled_matrices[0] != 0).astype(int)
        for matrix in scaled_matrices[1:]:
            sparsity_mask = sparsity_mask + (matrix != 0).astype(int)

        sparsity_mask.data[:] = 1

        num_matrices = len(scaled_matrices)
        random_factors = np.random.rand(num_matrices)
        random_factors /= np.sum(random_factors)

        new_matrix = sp.csr_matrix((desired_rows, desired_cols))
        for factor, matrix in zip(random_factors, scaled_matrices):
            temp = matrix.multiply(factor)
            new_matrix = new_matrix + temp

        output_directory = filedialog.askdirectory(title="Select Directory to Save New Matrix")
        if not output_directory:
            messagebox.showwarning("Save Cancelled", "Matrix generation cancelled.")
            return

        output_file_path = os.path.join(output_directory, "generated_matrix.mtx")
        scipy.io.mmwrite(output_file_path, new_matrix)

        generated_matrix = scipy.io.mmread(output_file_path).tocsr()
        generated_features = compute_features(generated_matrix)

        update_metadata_labels({'name': 'Generated Matrix', 'id': '-', 'date': '-', 'author': '-', 'ed': '-', 'kind': '-'})

        loaded_matrices = [generated_matrix]
        computed_features_list = [generated_features]

        draw_matrix_image(generated_matrix, matrix_image_frame)

        messagebox.showinfo("Success", f"New matrix generated and saved to {output_file_path}.")

    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", f"An error occurred: {e}")

def scale_matrix(matrix, desired_rows, desired_cols, tol=1e-4, max_iters=100):
    """
    Scale a sparse matrix to achieve balanced row and column norms close to 1, 
    and resize it to the desired dimensions.
    
    Parameters:
    - matrix: scipy.sparse.csr_matrix, the original matrix to scale
    - desired_rows: int, target number of rows in the scaled matrix
    - desired_cols: int, target number of columns in the scaled matrix
    - tol: float, tolerance level for convergence (default: 1e-4)
    - max_iters: int, maximum number of scaling iterations (default: 100)
    
    Returns:
    - scaled_matrix: scipy.sparse.csr_matrix, scaled and resized matrix
    """
    # Initialize a matrix of desired size with the values from the original matrix
    scaled_matrix = sp.lil_matrix((desired_rows, desired_cols))

    # Define scaling factors
    original_rows, original_cols = matrix.shape
    row_scale = desired_rows / original_rows
    col_scale = desired_cols / original_cols

    # Place values into the new scaled matrix using scaling factors
    for i, j in zip(*matrix.nonzero()):
        new_i = int(i * row_scale)
        new_j = int(j * col_scale)
        if new_i < desired_rows and new_j < desired_cols:
            scaled_matrix[new_i, new_j] = matrix[i, j]

    # Convert to CSR for efficient row/column operations
    scaled_matrix = scaled_matrix.tocsr()

    # Iteratively adjust row and column norms
    for _ in range(max_iters):
        # Row and column norms
        row_norms = np.array(scaled_matrix.sum(axis=1)).flatten()
        col_norms = np.array(scaled_matrix.sum(axis=0)).flatten()
        
        # Compute scaling factors
        row_scaling_factors = np.sqrt(1.0 / (row_norms + 1e-10))
        col_scaling_factors = np.sqrt(1.0 / (col_norms + 1e-10))
        
        # Scale rows
        for i in range(desired_rows):
            scaled_matrix.data[scaled_matrix.indptr[i]:scaled_matrix.indptr[i + 1]] *= row_scaling_factors[i]
        
        # Scale columns
        scaled_matrix = scaled_matrix.transpose().tocsr()
        for i in range(desired_cols):
            scaled_matrix.data[scaled_matrix.indptr[i]:scaled_matrix.indptr[i + 1]] *= col_scaling_factors[i]
        scaled_matrix = scaled_matrix.transpose().tocsr()

        # Check convergence (difference in norms close to zero)
        max_row_diff = np.abs(row_norms - 1).max()
        max_col_diff = np.abs(col_norms - 1).max()
        if max(max_row_diff, max_col_diff) < tol:
            break

    return scaled_matrix

def test_scale_matrix():
    # Function to test the scale_matrix function
    if len(loaded_matrices) == 0:
        messagebox.showerror("No Matrices Loaded", "Please load matrices to test scaling.")
        return

    # Get desired dimensions from the user
    user_rows = simpledialog.askinteger("Input", "Enter desired number of rows:")
    user_cols = simpledialog.askinteger("Input", "Enter desired number of columns:")

    if user_rows is None or user_cols is None:
        messagebox.showwarning("Input Error", "Please specify desired dimensions for scaling.")
        return

    try:
        scaled_matrix = scale_matrix(loaded_matrices[0], user_rows, user_cols)
        
        # Ask user for output directory to save the scaled matrix
        output_directory = filedialog.askdirectory(title="Select Directory to Save Scaled Matrix")
        if not output_directory:
            messagebox.showwarning("Save Cancelled", "Matrix scaling cancelled.")
            return

        # Save the scaled matrix to a file
        output_file_path = os.path.join(output_directory, "scaled_matrix.mtx")
        scipy.io.mmwrite(output_file_path, scaled_matrix)

        messagebox.showinfo("Success", f"Matrix scaled successfully and saved to {output_file_path}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while scaling: {e}")

# Create the main window
root = create_main_window()

# Create GUI components
dir_label = create_directory_frame(root, select_directory)
file_listbox = create_file_listbox(root)
rows_entry, cols_entry = create_dimension_input_frame(root)
generate_button, inspect_button = create_buttons(root, load_selected_files, generate_new_matrix, show_features_window)
metadata_frame, name_label, id_label, date_label, author_label, ed_label, kind_label = create_metadata_frame(root)
matrix_image_frame = create_matrix_image_frame(metadata_frame)
scale_button = tk.Button(root, text="Scale Matrix", command=test_scale_matrix)  # Add the Scale button
scale_button.pack()  # Adjust the packing as necessary for your layout

# Run the application
root.mainloop()
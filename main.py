import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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

        draw_matrix_image(matrices[0])
    else:
        messagebox.showwarning("Selection Error", "Please select files from the list.")

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

def draw_matrix_image(matrix):
    for widget in matrix_image_frame.winfo_children():
        widget.destroy()

    frame_width = matrix_image_frame.winfo_width()
    frame_height = matrix_image_frame.winfo_height()
    dpi = 100  
    fig_width = frame_width / dpi
    fig_height = frame_height / dpi

    fig = Figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax = fig.add_subplot(111)
    ax.spy(matrix, markersize=1)
    ax.set_title('Matrix Visualization')
    ax.axis('off')  

    canvas = FigureCanvasTkAgg(fig, master=matrix_image_frame)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
    matrix_image_frame.grid_propagate(False)

def show_features_window():
    features_window = tk.Toplevel(root)
    features_window.title("Matrix Features")
    features_window.geometry("600x400")

    tree = ttk.Treeview(features_window, columns=('Feature', 'Value'), show='headings')
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
        tree.insert('', tk.END, values=(key, value))

    scrollbar = ttk.Scrollbar(features_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree.pack(expand=True, fill=tk.BOTH)

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

        draw_matrix_image(generated_matrix)

        messagebox.showinfo("Success", f"New matrix generated and saved to {output_file_path}.")

    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Error", f"An error occurred: {e}")

def scale_matrix(matrix, desired_rows, desired_cols):
    # Create a new lil_matrix with the desired dimensions
    new_matrix = sp.lil_matrix((desired_rows, desired_cols))

    # Get the original matrix's shape
    original_rows, original_cols = matrix.shape

    # Determine the scaling factors
    row_scale = desired_rows / original_rows
    col_scale = desired_cols / original_cols

    # Fill the new matrix with values from the original matrix
    for i, j in zip(*matrix.nonzero()):
        new_i = int(i * row_scale)
        new_j = int(j * col_scale)
        if new_i < desired_rows and new_j < desired_cols:
            new_matrix[new_i, new_j] = matrix[i, j]

    # Convert back to csr_matrix for efficient operations
    return new_matrix.tocsr()

# Create the main window
root = create_main_window()

# Create GUI components
dir_label = create_directory_frame(root, select_directory)
file_listbox = create_file_listbox(root)
rows_entry, cols_entry = create_dimension_input_frame(root)
generate_button, inspect_button = create_buttons(root, load_selected_files, generate_new_matrix, show_features_window)
metadata_frame, name_label, id_label, date_label, author_label, ed_label, kind_label = create_metadata_frame(root)
matrix_image_frame = create_matrix_image_frame(metadata_frame)

# Run the application
root.mainloop()

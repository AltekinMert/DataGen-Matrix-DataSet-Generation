import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def create_main_window():
    root = tk.Tk()
    root.title("Matrix GUI")
    root.geometry("800x700")  # Adjusted window size
    return root

def create_directory_frame(root, select_directory):
    dir_frame = tk.Frame(root)
    dir_frame.pack(pady=10)

    dir_label = tk.Label(dir_frame, width=50, anchor="center", relief="sunken", text="Choose the directory containing .mtx files")
    dir_label.pack(side=tk.LEFT, padx=5)

    dir_select_button = tk.Button(dir_frame, text="Choose Directory", command=select_directory)
    dir_select_button.pack(side=tk.LEFT, padx=5)

    return dir_label

def create_file_listbox(root):
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)

    file_listbox = tk.Listbox(file_frame, height=10, width=50, selectmode=tk.MULTIPLE)
    file_listbox.pack(side=tk.LEFT, padx=5)

    listbox_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=file_listbox.yview)
    file_listbox.configure(yscroll=listbox_scrollbar.set)
    listbox_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    return file_listbox

def create_dimension_input_frame(root):
    dimension_frame = tk.Frame(root)
    dimension_frame.pack(pady=5)

    rows_label = tk.Label(dimension_frame, text="Desired Rows:")
    rows_label.pack(side=tk.LEFT, padx=5)
    rows_entry = tk.Entry(dimension_frame, width=10)
    rows_entry.pack(side=tk.LEFT, padx=5)

    cols_label = tk.Label(dimension_frame, text="Desired Columns:")
    cols_label.pack(side=tk.LEFT, padx=5)
    cols_entry = tk.Entry(dimension_frame, width=10)
    cols_entry.pack(side=tk.LEFT, padx=5)

    return rows_entry, cols_entry

def create_buttons(root, load_selected_files, generate_new_matrix, show_features_window):
    load_button = tk.Button(root, text="Load Selected Files", command=load_selected_files)
    load_button.pack(pady=5)

    generate_button = tk.Button(root, text="Generate New Matrix", command=generate_new_matrix, state=tk.DISABLED)
    generate_button.pack(pady=5)

    inspect_button = tk.Button(root, text="Inspect Features", command=show_features_window, state=tk.DISABLED)
    inspect_button.pack(pady=5)

    return generate_button, inspect_button

def create_metadata_frame(root):
    content_frame = tk.Frame(root)
    content_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    content_frame.rowconfigure(0, weight=1)

    metadata_frame = tk.LabelFrame(content_frame, text="Matrix Metadata", width=400, height=400)
    metadata_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    metadata_frame.grid_propagate(False)  # Prevent resizing

    # Create labels for metadata
    name_label = tk.Label(metadata_frame, text="Name: -", anchor='w')
    name_label.grid(row=0, column=0, sticky='w', padx=10, pady=2)

    id_label = tk.Label(metadata_frame, text="ID: -", anchor='w')
    id_label.grid(row=1, column=0, sticky='w', padx=10, pady=2)

    date_label = tk.Label(metadata_frame, text="Date: -", anchor='w')
    date_label.grid(row=2, column=0, sticky='w', padx=10, pady=2)

    author_label = tk.Label(metadata_frame, text="Author: -", anchor='w')
    author_label.grid(row=3, column=0, sticky='w', padx=10, pady=2)

    ed_label = tk.Label(metadata_frame, text="Ed: -", anchor='w')
    ed_label.grid(row=4, column=0, sticky='w', padx=10, pady=2)

    kind_label = tk.Label(metadata_frame, text="Kind: -", anchor='w')
    kind_label.grid(row=5, column=0, sticky='w', padx=10, pady=2)

    return metadata_frame, name_label, id_label, date_label, author_label, ed_label, kind_label

def create_matrix_image_frame(content_frame):
    matrix_image_frame = tk.Frame(content_frame, bg="white", relief="sunken", width=400, height=400)
    matrix_image_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
    matrix_image_frame.grid_propagate(False)  # Prevent resizing
    return matrix_image_frame
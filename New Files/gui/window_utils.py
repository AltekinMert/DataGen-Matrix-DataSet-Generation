import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import os
from functional.mtx_inspection import (
    load_mtx_file,
    get_basic_properties,
    get_symmetry,
    get_nonzeros_per_row_stats,
    get_nonzeros_per_col_stats,
    get_nonzero_value_stats,
    get_row_statistics,
    get_col_statistics,
    get_distance_to_diagonal,
    get_structural_unsymmetry,
    get_matrix_norms,
    get_condition_number
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_DIM = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"  # 800x600
FONT = "Arial"
FONT_SIZE = 14

def setup_close_behavior(window, root):
    """
    Sets up behavior for the close button (WM_DELETE_WINDOW) on a secondary window.
    
    Parameters:
        window (tk.Toplevel): The secondary window.
        root (tk.Tk): The main application window.
    """
    def on_close():
        root.deiconify()  # Show the main window
        window.destroy()  # Destroy the current window
    window.protocol("WM_DELETE_WINDOW", on_close)

def add_back_to_main_button(window, root, pos_x, pos_y, button_width, button_height):
    """
    Adds a "Go to Main Menu" button to a tkinter window.
    
    Parameters:
        window (tk.Toplevel): The secondary window where the button will be added.
        root (tk.Tk): The main application window.
    """
    def go_back():
        window.destroy()  # Close the current window
        root.deiconify()  # Show the main window
    button = tk.Button(window, text="Go to Main Menu", command=go_back, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

def add_placeholder(entry, placeholder_text):
    """
    Adds placeholder functionality to a tkinter Entry widget.
    
    Parameters:
        entry (tk.Entry): The Entry widget to add the placeholder to.
        placeholder_text (str): The placeholder text to display.
    """
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)  # Remove placeholder
            entry.config(fg="black")  # Set text color to black

    def on_focus_out(event):
        if entry.get() == "":  # If empty, restore placeholder
            entry.insert(0, placeholder_text)
            entry.config(fg="grey")

    # Initialize placeholder
    entry.insert(0, placeholder_text)  # Set placeholder text
    entry.config(fg="grey")  # Set placeholder text color
    entry.bind("<FocusIn>", on_focus_in)  # Bind focus-in event
    entry.bind("<FocusOut>", on_focus_out)  # Bind focus-out event

def add_folder_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    folder_var = tk.StringVar()
    folder_var.set("No folder selected")
    current_text = tk.StringVar()
    current_text.set(button_text)

    def select_folder():
        folder_path = filedialog.askdirectory()
        if folder_path:
            folder_var.set(folder_path)
            folder_name = folder_path if len(folder_path) <= 24 else folder_path[-24:]
            current_text.set(folder_name)
            button.config(text=folder_name)

    def on_hover(event):
        button.config(text="Click to select a folder")

    def on_leave(event):
        button.config(text=current_text.get())

    button = tk.Button(parent, text=button_text, command=select_folder, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return folder_var

def add_file_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    file_var = tk.StringVar()
    file_var.set("No file selected")
    current_text = tk.StringVar()
    current_text.set(button_text)

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Matrix files", "*.mtx"), ("All files", "*.*")]
        )
        if file_path:
            file_var.set(file_path)
            file_name = file_path.split("/")[-1]
            new_text = file_name if len(file_name) <= 30 else file_name[:27] + "..."
            current_text.set(new_text)
            button.config(text=new_text)

    def on_hover(event):
        button.config(text="Click to select a file")

    def on_leave(event):
        button.config(text=current_text.get())

    button = tk.Button(parent, text=button_text, command=select_file, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return file_var

uploaded_file_path = None

def upload_selected_file(file_listbox):
    global uploaded_file_path
    try:
        selected_index = file_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No File Selected", "Please select a file from the list.")
            return None
        
        selected_file = file_listbox.get(selected_index)
        folder_path = file_listbox.folder_path

        if not folder_path:
            messagebox.showerror("Folder Error", "No folder associated with the listbox.")
            return None

        uploaded_file_path = os.path.join(folder_path, selected_file)
        messagebox.showinfo("File Uploaded", f"File uploaded: {selected_file}")

        return uploaded_file_path
    except Exception as e:
        messagebox.showerror("Upload Error", f"An error occurred: {e}")
        return None

def open_matrix_graph_window(table_window, matrix):
    graph_window = tk.Toplevel()
    graph_window.geometry(WINDOW_DIM)
    graph_window.title("Matrix Graph")

    def on_close():
        table_window.deiconify()
        graph_window.destroy()

    graph_window.protocol("WM_DELETE_WINDOW", on_close)

    table_window.withdraw()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.spy(matrix, markersize=1)
    ax.set_title("Matrix Graph", fontsize=14)
    ax.set_xlabel("Columns", fontsize=12)
    ax.set_ylabel("Rows", fontsize=12)

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

def open_matrix_heatmap_window(table_window, matrix):
    heatmap_window = tk.Toplevel()
    heatmap_window.geometry(WINDOW_DIM)
    heatmap_window.title("Matrix Heatmap")

    def on_close():
        table_window.deiconify()
        heatmap_window.destroy()

    heatmap_window.protocol("WM_DELETE_WINDOW", on_close)

    table_window.withdraw()

    matrix_min = np.min(matrix)
    matrix_max = np.max(matrix)
    normalized_matrix = (matrix - matrix_min) / (matrix_max - matrix_min) if matrix_max > matrix_min else np.zeros_like(matrix)

    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(normalized_matrix, cmap='viridis')
    fig.colorbar(cax)

    ax.set_title("Matrix Heatmap", pad=20, fontsize=14)
    ax.set_xlabel("Columns", fontsize=12)
    ax.set_ylabel("Rows", fontsize=12)

    canvas = FigureCanvasTkAgg(fig, master=heatmap_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

def open_matrix_inspection_window(generate_window):
    global uploaded_file_path
    if not uploaded_file_path:
        messagebox.showwarning("No File Uploaded", "Please upload a file before inspecting the matrix.")
        return

    matrix = load_mtx_file(uploaded_file_path)
    if matrix is None:
        messagebox.showerror("Error", "Failed to load the matrix from the uploaded file.")
        return

    inspection_window = tk.Toplevel()
    inspection_window.geometry(WINDOW_DIM)
    inspection_window.title("Matrix Inspection")

    def on_close():
        generate_window.deiconify()
        inspection_window.destroy()

    inspection_window.protocol("WM_DELETE_WINDOW", on_close)

    generate_window.withdraw()

    tree = ttk.Treeview(inspection_window, show="headings")
    tree["columns"] = ("Property", "Value")
    tree.heading("Property", text="Property")
    tree.heading("Value", text="Value")
    tree.column("Property", width=300)
    tree.column("Value", width=200)

    formal_property_names = {
        "num_rows": "Number of Rows",
        "num_cols": "Number of Columns",
        "num_nonzeros": "Number of Nonzeros",
        "density_percent": "Density (%)",
        "pattern_symmetry": "Pattern Symmetry",
        "numerical_symmetry": "Numerical Symmetry",
        "nonzeros_per_row_min": "Minimum Nonzeros per Row",
        "nonzeros_per_row_max": "Maximum Nonzeros per Row",
        "nonzeros_per_row_avg": "Average Nonzeros per Row",
        "nonzeros_per_row_std": "Standard Deviation of Nonzeros per Row",
        "nonzeros_per_col_min": "Minimum Nonzeros per Column",
        "nonzeros_per_col_max": "Maximum Nonzeros per Column",
        "nonzeros_per_col_avg": "Average Nonzeros per Column",
        "nonzeros_per_col_std": "Standard Deviation of Nonzeros per Column",
        "value_min": "Minimum Value",
        "value_max": "Maximum Value",
        "value_avg": "Average Value",
        "value_std": "Standard Deviation of Values",
        "avg_distance_to_diagonal": "Average Distance to Diagonal",
        "num_diagonals_with_nonzeros": "Number of Diagonals with Nonzeros",
        "bandwidth": "Bandwidth",
        "num_structurally_unsymmetric_elements": "Number of Structurally Unsymmetric Elements",
        "norm_1": "1-Norm",
        "norm_inf": "Infinity Norm",
        "frobenius_norm": "Frobenius Norm",
        "estimated_condition_number": "Estimated Condition Number",
    }

    def add_properties_to_tree(property_dict):
        for key, value in property_dict.items():
            formal_name = formal_property_names.get(key, key.replace("_", " ").title())
            tree.insert("", "end", values=(formal_name, value))

    add_properties_to_tree(get_basic_properties(matrix))
    add_properties_to_tree(get_symmetry(matrix))
    add_properties_to_tree(get_nonzeros_per_row_stats(matrix))
    add_properties_to_tree(get_nonzeros_per_col_stats(matrix))
    add_properties_to_tree(get_nonzero_value_stats(matrix))
    add_properties_to_tree(get_distance_to_diagonal(matrix))
    add_properties_to_tree(get_structural_unsymmetry(matrix))
    add_properties_to_tree(get_matrix_norms(matrix))
    add_properties_to_tree(get_condition_number(matrix))

    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_show_matrix_graph():
        open_matrix_graph_window(inspection_window, matrix)

    def on_show_matrix_heatmap():
        open_matrix_heatmap_window(inspection_window, matrix)

    button_frame = tk.Frame(inspection_window)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    graph_button = tk.Button(
        button_frame, text="Show Matrix Graph", font=(FONT, FONT_SIZE),
        command=on_show_matrix_graph
    )
    graph_button.pack(side=tk.LEFT, expand=True, padx=5)

    heatmap_button = tk.Button(
        button_frame, text="Show Matrix Heatmap", font=(FONT, FONT_SIZE),
        command=on_show_matrix_heatmap
    )
    heatmap_button.pack(side=tk.LEFT, expand=True, padx=5)
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
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
import matplotlib.colors as mcolors
import numpy as np

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_DIM = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}" # 800x600
FONT = "Arial"
FONT_SIZE = 14

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
            entry.config(fg="white")  # Set text color to black

    def on_focus_out(event):
        if entry.get() == "":  # If empty, restore placeholder
            entry.insert(0, placeholder_text)
            entry.config(fg="white")

    # Initialize placeholder
    entry.insert(0, placeholder_text)  # Set placeholder text
    entry.config(fg="white")  # Set placeholder text color
    entry.bind("<FocusIn>", on_focus_in)  # Bind focus-in event
    entry.bind("<FocusOut>", on_focus_out)  # Bind focus-out event

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
        pos_x (int): The x position of the button
        pos_y (int): The y position of the button
        button_width (int): The width of the button
        button_height (int): The height of the button
    """
    def go_back():
        window.destroy()  # Close the current window
        root.deiconify()  # Show the main window

    button = tk.Button(window, text="Go to Main Menu", command=go_back, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

def add_folder_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    """
    Adds a folder selector button and a label to display the selected folder.

    Parameters:
        parent (tk.Toplevel): The window where the button will be added.
        button_text (str): The default text for the folder selector button.
        pos_x (int): The x position of the button.
        pos_y (int): The y position of the button.
        button_width (int): The width of the button.
        button_height (int): The height of the button.

    Returns:
        tk.StringVar: A StringVar that holds the selected folder path.
    """
    folder_var = tk.StringVar()
    folder_var.set("No folder selected")  # Default message
    current_text = tk.StringVar()  # To track the button's current state
    current_text.set(button_text)

    def select_folder():
        folder_path = filedialog.askdirectory()  # Open folder selection dialog
        if folder_path:
            folder_var.set(folder_path)  # Update the folder path
            folder_name = folder_path if len(folder_path) <= 24 else folder_path[len(folder_path) - 24:]
            current_text.set(folder_name)  # Update button text to show folder name
            button.config(text=folder_name)

    def on_hover(event):
        button.config(text="Click to select a folder")

    def on_leave(event):
        button.config(text=current_text.get())  # Restore the current button text

    # Create button
    button = tk.Button(parent, text=button_text, command=select_folder, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    # Bind hover events
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return folder_var

def add_file_selector(parent, button_text, pos_x, pos_y, button_width, button_height):
    """
    Adds a file selector button and a label to display the selected file.

    Parameters:
        parent (tk.Toplevel): The window where the button will be added.
        button_text (str): The default text for the file selector button.
        pos_x (int): The x position of the button.
        pos_y (int): The y position of the button.
        button_width (int): The width of the button.
        button_height (int): The height of the button.

    Returns:
        tk.StringVar: A StringVar that holds the selected file path.
    """
    file_var = tk.StringVar()
    file_var.set("No file selected")  # Default message
    current_text = tk.StringVar()  # To track the button's current state
    current_text.set(button_text)

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[("Matrix files", "*.mtx"), ("All files", "*.*")]
        )
        if file_path:
            file_var.set(file_path)  # Update the selected file path
            file_name = file_path.split("/")[-1]  # Extract file name from the path
            new_text = file_name if len(file_name) <= 30 else file_name[:27] + "..."
            current_text.set(new_text)  # Update button text to show file name
            button.config(text=new_text)

    def on_hover(event):
        button.config(text="Click to select a file")

    def on_leave(event):
        button.config(text=current_text.get())  # Restore the current button text

    # Create button
    button = tk.Button(parent, text=button_text, command=select_file, font=(FONT, FONT_SIZE))
    button.place(x=pos_x, y=pos_y, width=button_width, height=button_height)

    # Bind hover events
    button.bind("<Enter>", on_hover)
    button.bind("<Leave>", on_leave)

    return file_var

uploaded_file_path = None  # Global variable to store the uploaded file path

def upload_selected_file(file_listbox):
    """
    Handles the upload of the selected file from the listbox.

    Parameters:
        file_listbox (tk.Listbox): The Listbox widget containing the file list.

    Returns:
        str: The path of the uploaded file, or None if no file is selected.
    """
    global uploaded_file_path
    try:
        selected_index = file_listbox.curselection()  # Get the selected item index
        if not selected_index:
            tk.messagebox.showwarning("No File Selected", "Please select a file from the list.")
            return None
        
        selected_file = file_listbox.get(selected_index)  # Get the selected file name
        folder_path = file_listbox.folder_path  # Custom attribute to store folder path

        if not folder_path:
            tk.messagebox.showerror("Folder Error", "No folder associated with the listbox.")
            return None

        # Construct the full path of the selected file
        uploaded_file_path = os.path.join(folder_path, selected_file)
        tk.messagebox.showinfo("File Uploaded", f"File uploaded: {selected_file}")

        return uploaded_file_path
    except Exception as e:
        tk.messagebox.showerror("Upload Error", f"An error occurred: {e}")
        return None

def open_matrix_graph_window(table_window, matrix):
    """
    Opens a new window to display the graph of the matrix using matplotlib.

    Parameters:
        table_window (tk.Toplevel): The table window to return to on close.
        matrix (np.ndarray): The matrix to be visualized as a graph.
    """
    # Create a new Toplevel window for the graph
    graph_window = tk.Toplevel()
    graph_window.geometry(WINDOW_DIM)
    graph_window.title("Matrix Graph")

    # Setup close behavior to return to the table view
    def on_close():
        table_window.deiconify()  # Show the table window
        graph_window.destroy()  # Destroy the graph window

    graph_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hide the table window
    table_window.withdraw()

    # Create the graph using matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.spy(matrix, markersize=1)  # Use the spy plot for matrix visualization
    ax.set_title("Matrix Graph", fontsize=14)
    ax.set_xlabel("Columns", fontsize=12)
    ax.set_ylabel("Rows", fontsize=12)

    # Embed the matplotlib figure into the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

def open_matrix_heatmap_window(table_window, matrix):
    """
    Opens a new window to display the heatmap of the matrix using matplotlib.
    Normalizes the matrix values between 0 and 1 before visualization.

    Parameters:
        table_window (tk.Toplevel): The table window to return to on close.
        matrix (np.ndarray): The matrix to be visualized as a heatmap.
    """
    # Create a new Toplevel window for the heatmap
    heatmap_window = tk.Toplevel()
    heatmap_window.geometry(WINDOW_DIM)
    heatmap_window.title("Matrix Heatmap")

    # Setup close behavior to return to the table view
    def on_close():
        table_window.deiconify()  # Show the table window
        heatmap_window.destroy()  # Destroy the heatmap window

    heatmap_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hide the table window
    table_window.withdraw()

    # Normalize the matrix between 0 and 1
    matrix_min = np.min(matrix)
    matrix_max = np.max(matrix)
    if matrix_max > matrix_min:  # Avoid division by zero
        normalized_matrix = (matrix - matrix_min) / (matrix_max - matrix_min)
    else:
        normalized_matrix = np.zeros_like(matrix)  # If all values are the same, set to 0

    # Create the heatmap using matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(normalized_matrix, cmap='viridis')  # Use a color map for visualization
    fig.colorbar(cax)  # Add a color bar to indicate intensity

    ax.set_title("Matrix Heatmap", pad=20, fontsize=14)
    ax.set_xlabel("Columns", fontsize=12)
    ax.set_ylabel("Rows", fontsize=12)

    # Embed the matplotlib figure into the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=heatmap_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

def open_matrix_inspection_window(generate_window):
    """
    Opens a new window for inspecting a matrix and populates it with extracted properties.

    Parameters:
        generate_window (tk.Toplevel): The generate window to return to on close.
    """
    global uploaded_file_path
    if not uploaded_file_path:
        tk.messagebox.showwarning("No File Uploaded", "Please upload a file before inspecting the matrix.")
        return

    # Load the matrix from the uploaded file
    matrix = load_mtx_file(uploaded_file_path)
    if matrix is None:
        tk.messagebox.showerror("Error", "Failed to load the matrix from the uploaded file.")
        return

    # Create the inspection window
    inspection_window = tk.Toplevel()
    inspection_window.geometry(WINDOW_DIM)
    inspection_window.title("Matrix Inspection")

    # Setup close behavior to return to generate_window
    def on_close():
        generate_window.deiconify()  # Show the generate window
        inspection_window.destroy()  # Destroy the inspection window

    inspection_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hide the generate_window
    generate_window.withdraw()

    # Create a table (Treeview) in the new window
    tree = ttk.Treeview(inspection_window, show="headings")  # Remove the ID column
    tree["columns"] = ("Property", "Value")
    tree.heading("Property", text="Property")
    tree.heading("Value", text="Value")
    tree.column("Property", width=300)
    tree.column("Value", width=200)

    # Formal property names mapping
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
        """Helper function to add properties to the Treeview."""
        for key, value in property_dict.items():
            formal_name = formal_property_names.get(key, key.replace("_", " ").title())
            tree.insert("", "end", values=(formal_name, value))

    # Extract properties and populate the table
    add_properties_to_tree(get_basic_properties(matrix))
    add_properties_to_tree(get_symmetry(matrix))
    add_properties_to_tree(get_nonzeros_per_row_stats(matrix))
    add_properties_to_tree(get_nonzeros_per_col_stats(matrix))
    add_properties_to_tree(get_nonzero_value_stats(matrix))
    add_properties_to_tree(get_distance_to_diagonal(matrix))
    add_properties_to_tree(get_structural_unsymmetry(matrix))
    add_properties_to_tree(get_matrix_norms(matrix))
    add_properties_to_tree(get_condition_number(matrix))

    # Position the table in the window
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add buttons below the table
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
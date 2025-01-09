import tkinter as tk
from gui.window_utils import (
    add_placeholder,
    setup_close_behavior,
    add_file_selector,
    add_folder_selector,
    add_back_to_main_button
)
from functional.dynamic_matrix_expansion import create_multiple_matrices
from gui.create_progress import open_create_progress_window

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_DIM = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
FONT = "Arial"
FONT_SIZE = 14

def open_create_window(root):
    """
    Opens the Create Window for matrix creation inputs and parameters.

    Parameters:
        root (tk.Tk): The main application window.
    """
    # Create a new Toplevel window
    window = tk.Toplevel()
    window.geometry(WINDOW_DIM)
    window.title("Create New Matrices")

    # Set up close behavior
    setup_close_behavior(window, root)

    # Entry fields for user inputs
    entry1 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry1.place(x=50, y=50, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
    add_placeholder(entry1, "Desired row number")

    entry2 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry2.place(x=50, y=125, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
    add_placeholder(entry2, "Desired column number")

    entry3 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry3.place(x=50, y=200, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
    add_placeholder(entry3, "Desired density")

    entry4 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry4.place(x=50, y=275, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
    add_placeholder(entry4, "Desired number of matrices to be created")

    # Add file selector
    file_var = add_file_selector(
        window,
        button_text="Select MTX File",
        pos_x=400, pos_y=50,
        button_width=BUTTON_WIDTH, button_height=BUTTON_HEIGHT
    )

    # Add folder selector
    folder_var = add_folder_selector(
        window,
        button_text="Select Folder to Save Matrices",
        pos_x=400, pos_y=125,
        button_width=BUTTON_WIDTH, button_height=BUTTON_HEIGHT
    )

    # Behavior of Create button
    def on_create_button_click():
        try:
            file_path = file_var.get()
            output_directory = folder_var.get()
            rows = int(entry1.get())
            cols = int(entry2.get())
            density = int(entry3.get())
            num = int(entry4.get())

            open_create_progress_window(
                parent_window=window,
                file_path=file_path,
                output_directory=output_directory,
                rows=rows,
                cols=cols,
                density=density,
                num=num
            )
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please provide valid numeric values for all fields.")

    # Add Create button
    create_button = tk.Button(window, text="Create", font=(FONT, FONT_SIZE), command=on_create_button_click)
    create_button.place(x=400, y=275, width=BUTTON_WIDTH / 2, height=BUTTON_HEIGHT)

    # Add "Go Back to Main Menu" button
    add_back_to_main_button(window, root, pos_x=50, pos_y=525, button_width=BUTTON_WIDTH / 2, button_height=BUTTON_HEIGHT)
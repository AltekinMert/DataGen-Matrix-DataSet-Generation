import os
import tkinter as tk
from gui.window_utils import *

# Buttonlıarın konum ve dimensionlarını elle kodladın - düzelt

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50

def open_generate_window(root):
    window = tk.Toplevel()
    window.geometry(WINDOW_DIM)
    window.title("Generate new matrices with Neural Network")

    # Set up close behavior
    setup_close_behavior(window, root)

    # Function to update the file list
    def update_file_list(folder_path):
        file_list.delete(0, tk.END)  # Clear the current list
        if folder_path and os.path.isdir(folder_path):
            files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
            for file in files:
                file_list.insert(tk.END, file)  # Add each file to the Listbox
            file_list.folder_path = folder_path  # Store the folder path as an attribute of the Listbox

    # Add folder selector
    def folder_selected_callback():
        folder_path = folder_var.get()
        update_file_list(folder_path)

    folder_var = add_folder_selector(
        window,
        button_text="Click to select a folder",
        pos_x=50, pos_y=50,
        button_width=BUTTON_WIDTH, button_height=BUTTON_HEIGHT
    )

    # Bind the folder selection callback directly
    folder_var.trace_add("write", lambda *args: folder_selected_callback())

    # Add a listbox to display files
    file_list = tk.Listbox(window, font=(FONT, FONT_SIZE))
    file_list.place(x=50, y=150, width=BUTTON_WIDTH + 100, height=BUTTON_HEIGHT * 3)

    button = tk.Button(window, text="Upload the file", font=(FONT, FONT_SIZE), command=lambda: upload_selected_file(file_list))
    button.place(x=500, y=150, width=BUTTON_WIDTH / 2, height=60)

    button = tk.Button(window, text="Inspect the matrix", font=(FONT, FONT_SIZE), command=lambda: open_matrix_inspection_window(window))
    button.place(x=500, y=240, width=BUTTON_WIDTH / 2, height=60)

    # Create three entry fields with placeholders
    entry1 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry1.place(x=50, y=350, width=BUTTON_WIDTH + 100, height=BUTTON_HEIGHT)
    add_placeholder(entry1, "Desired row number")

    entry2 = tk.Entry(window, font=(FONT, FONT_SIZE))
    entry2.place(x=50, y=425, width=BUTTON_WIDTH + 100, height=BUTTON_HEIGHT)
    add_placeholder(entry2, "Desired column number")

    button = tk.Button(window, text="Start the training", font=(FONT, FONT_SIZE))
    button.place(x=500, y=350, width=BUTTON_WIDTH / 2, height=125)

    # Add "Go Back to Main Menu" button
    add_back_to_main_button(window, root, pos_x=50, pos_y=525, button_width=BUTTON_WIDTH / 2, button_height=BUTTON_HEIGHT)
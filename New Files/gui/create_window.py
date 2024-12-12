import tkinter as tk
from gui.window_utils import *
from functional.dynamic_matrix_expansion import *

# Entry ve buttonlar için aynı width ve height kullanılıyor - düzelt
# Entyler sadece sayısal değer kabul etmeli
# Matrix inceleme butonu ekle

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50

def open_create_window(root):
    window = tk.Toplevel()
    window.geometry(WINDOW_DIM)
    window.title("Create new matrices")

    # Set up close behavior
    setup_close_behavior(window, root)

    # Create three entry fields with placeholders
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
        button_text="Select MTX file", 
        pos_x=400, pos_y=50, 
        button_width=BUTTON_WIDTH, button_height=BUTTON_HEIGHT
    )

    # Add folder selector under the third entry
    folder_var = add_folder_selector(
        window, 
        button_text="Select a folder to save the matrices:", 
        pos_x=400, pos_y=125, 
        button_width=BUTTON_WIDTH, button_height=BUTTON_HEIGHT
    )

    # Behavior of create button
    def on_create_button_click(): 
        file_path = file_var.get()
        output_directory = folder_var.get()
        rows = int(entry1.get())
        cols = int(entry2.get())
        density = int(entry3.get())
        num = int(entry4.get())

        create_multiple_matrices(file_path, output_directory, rows, cols, density, num)
    
    # Add create button
    button = tk.Button(window, text="Create", font=(FONT, FONT_SIZE), command=on_create_button_click)
    button.place(x=400, y=275, width=BUTTON_WIDTH / 2, height=BUTTON_HEIGHT)

    # Add "Go Back to Main Menu" button
    add_back_to_main_button(window, root, pos_x=50, pos_y=525, button_width=BUTTON_WIDTH / 2, button_height=BUTTON_HEIGHT)
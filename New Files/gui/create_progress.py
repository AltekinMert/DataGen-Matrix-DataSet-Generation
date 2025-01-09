import tkinter as tk
from tkinter import ttk
from functional.dynamic_matrix_expansion import create_multiple_matrices
import os

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50
FONT = "Arial"
FONT_SIZE = 14
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
WINDOW_DIM = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

def open_create_progress_window(parent_window, file_path, output_directory, rows, cols, density, num):
    """
    Opens the progress window to show the progress of matrix creation.

    Parameters:
        parent_window (tk.Toplevel): The parent window to return to on close.
        file_path (str): Path to the input matrix file.
        output_directory (str): Folder to save the created matrices.
        rows (int): Desired number of rows for the matrices.
        cols (int): Desired number of columns for the matrices.
        density (int): Desired density of the matrices.
        num (int): Number of matrices to create.
    """
    # Create a new Toplevel window
    progress_window = tk.Toplevel()
    progress_window.geometry(WINDOW_DIM)
    progress_window.title("Matrix Creation Progress")
    progress_window.resizable(False, False)

    # Close behavior to return to parent_window
    def on_close():
        parent_window.deiconify()
        progress_window.destroy()

    progress_window.protocol("WM_DELETE_WINDOW", on_close)

    # Hide the parent window
    parent_window.withdraw()

    # Add a label to display the progress status
    progress_label = tk.Label(progress_window, text="Creating matrices...", font=(FONT, FONT_SIZE))
    progress_label.pack(pady=20)

    # Add a progress bar
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=20)
    progress_bar["maximum"] = num

    # Variables to track progress
    current_matrix = 0

    def create_next_matrix():
        nonlocal current_matrix
        if current_matrix < num:
            unique_output_dir = os.path.join(output_directory, f"matrix_{current_matrix + 1}.mtx")
            create_multiple_matrices(
                file_path=file_path,
                output_directory=output_directory,
                desired_rows=rows,
                desired_cols=cols,
                desired_density=density,
                desired_num=1
            )
            # Rename the generated file to ensure uniqueness
            os.rename(
                os.path.join(output_directory, "expanded_matrix_1.mtx"),
                unique_output_dir
            )

            # Update progress
            current_matrix += 1
            progress_bar["value"] = current_matrix
            progress_label.config(text=f"Creating matrices... ({current_matrix}/{num})")
            progress_window.after(100, create_next_matrix)  # Schedule the next matrix creation
        else:
            # Matrix creation complete
            progress_bar.pack_forget()  # Remove the progress bar
            progress_label.config(
                text="Matrix creation done!",
                font=(FONT, FONT_SIZE + 10),  # Bigger font size
                pady=50  # Center vertically
            )
            progress_label.pack(fill=tk.BOTH, expand=True)  # Center in the middle

            # Add a close button
            close_button = tk.Button(
                progress_window,
                text="Close",
                font=(FONT, FONT_SIZE),
                command=on_close
            )
            close_button.pack(pady=20)

    # Start the matrix creation process
    progress_window.after(100, create_next_matrix)
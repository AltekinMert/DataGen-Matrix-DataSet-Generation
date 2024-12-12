import matplotlib.pyplot as plt
from scipy.io import mmread
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Function to open a file dialog and select the .mtx file
def choose_file():
    Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
    file_path = askopenfilename(title="Select a Matrix Market (.mtx) file",
                                filetypes=[("Matrix Market files", "*.mtx")])
    return file_path

# Function to read and visualize the matrix from an .mtx file
def visualize_mtx_matrix():
    # Ask the user to select the file
    file_path = choose_file()

    if not file_path:
        print("No file selected.")
        return

    # Read the matrix from the selected mtx file
    matrix = mmread(file_path)

    # Convert the matrix to a dense array (if it's sparse)
    dense_matrix = matrix.toarray() if hasattr(matrix, 'toarray') else matrix

    # Plot the matrix
    plt.figure(figsize=(10, 10))
    plt.spy(dense_matrix, markersize=1)  # Spy plot to visualize the sparsity pattern
    plt.title('Matrix Visualization')
    plt.show()

# Call the function to visualize the matrix
visualize_mtx_matrix()
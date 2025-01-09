import scipy.io
from scipy.sparse import csr_matrix
import numpy as np
import os

def load_matrix(file_path):
    """
    Load a matrix from a .mtx file.

    Parameters:
        file_path (str): Path to the .mtx file.

    Returns:
        np.ndarray: Loaded matrix as a NumPy array.
    """
    try:
        matrix = scipy.io.mmread(file_path)
        return matrix.toarray() if hasattr(matrix, "toarray") else matrix
    except Exception as e:
        print(f"Error loading the matrix: {e}")
        return None

def expand_matrix(original_matrix, desired_rows, desired_cols, additional_density):
    """
    Expand a matrix by scaling and increasing non-zero density.

    Parameters:
        original_matrix (np.ndarray): The input sparse matrix to expand.
        desired_rows (int): Number of rows in the expanded matrix.
        desired_cols (int): Number of columns in the expanded matrix.
        additional_density (int): Number of new non-zeros to add around each scaled position.

    Returns:
        np.ndarray: The expanded matrix.
    """
    expanded_matrix = np.zeros((desired_rows, desired_cols))

    non_zero_positions = np.argwhere(original_matrix != 0)
    non_zero_values = original_matrix[original_matrix != 0]

    min_value = non_zero_values.min()
    max_value = non_zero_values.max()

    row_scale = desired_rows / original_matrix.shape[0]
    col_scale = desired_cols / original_matrix.shape[1]

    for i, (row, col) in enumerate(non_zero_positions):
        new_row = int(row * row_scale)
        new_col = int(col * col_scale)
        new_row = min(max(new_row, 0), desired_rows - 1)
        new_col = min(max(new_col, 0), desired_cols - 1)

        expanded_matrix[new_row, new_col] = non_zero_values[i]

        for _ in range(additional_density):
            jitter_row = np.random.randint(-3, 4)
            jitter_col = np.random.randint(-3, 4)
            jittered_row = min(max(new_row + jitter_row, 0), desired_rows - 1)
            jittered_col = min(max(new_col + jitter_col, 0), desired_cols - 1)
            if expanded_matrix[jittered_row, jittered_col] == 0:
                expanded_matrix[jittered_row, jittered_col] = np.random.uniform(min_value, max_value)

    return expanded_matrix

def create_multiple_matrices(file_path, output_directory, desired_rows, desired_cols, desired_density, desired_num):
    """
    Create multiple expanded matrices from an input matrix.

    Parameters:
        file_path (str): Path to the input matrix file.
        output_directory (str): Directory to save the expanded matrices.
        desired_rows (int): Desired number of rows in the expanded matrices.
        desired_cols (int): Desired number of columns in the expanded matrices.
        desired_density (int): Density of the expanded matrices.
        desired_num (int): Number of matrices to create.
    """
    os.makedirs(output_directory, exist_ok=True)
    original_matrix = load_matrix(file_path)

    if original_matrix is not None:
        for i in range(desired_num):
            expanded_matrix = expand_matrix(original_matrix, desired_rows, desired_cols, desired_density)
            save_path = os.path.join(output_directory, f"expanded_matrix_{i + 1}.mtx")
            scipy.io.mmwrite(save_path, csr_matrix(expanded_matrix))
    else:
        print("Failed to load the matrix.")
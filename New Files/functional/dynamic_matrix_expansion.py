import scipy.io
from scipy.sparse import csr_matrix
import numpy as np
import matplotlib.pyplot as plt
import os

def load_matrix(file_path):
    """Load a matrix from a .mtx file."""
    try:
        matrix = scipy.io.mmread(file_path)
        return matrix.toarray() if hasattr(matrix, "toarray") else matrix
    except Exception as e:
        print("Error loading the matrix:", e)
        return None

def expand_matrix(original_matrix, desired_rows, desired_cols, additional_density):
    """
    Expand the matrix by scaling original non-zero positions proportionally,
    preserving the pattern, and increasing non-zero count with controlled density.
    
    Parameters:
    - original_matrix: The input sparse matrix to expand.
    - desired_rows: Number of rows in the expanded matrix.
    - desired_cols: Number of columns in the expanded matrix.
    - additional_density: Number of new non-zeros to add around each scaled position.
    
    Returns:
    - expanded_matrix: The expanded matrix with increased non-zero count and preserved pattern.
    """
    # Create an empty matrix with desired dimensions
    expanded_matrix = np.zeros((desired_rows, desired_cols))
    
    # Identify non-zero positions and values in the original matrix
    non_zero_positions = np.argwhere(original_matrix != 0)
    non_zero_values = original_matrix[original_matrix != 0]
    
    # Min and max values of original non-zeros
    min_value = non_zero_values.min()
    max_value = non_zero_values.max()
    
    # Scaling factors for rows and columns
    row_scale = desired_rows / original_matrix.shape[0]
    col_scale = desired_cols / original_matrix.shape[1]
    
    for i, (row, col) in enumerate(non_zero_positions):
        # Scale positions to the new dimensions
        new_row = int(row * row_scale)
        new_col = int(col * col_scale)
        
        # Ensure positions stay within bounds and place the original non-zero
        new_row = min(max(new_row, 0), desired_rows - 1)
        new_col = min(max(new_col, 0), desired_cols - 1)
        expanded_matrix[new_row, new_col] = non_zero_values[i]
        
        # Add additional non-zeros around the scaled position
        for _ in range(additional_density):
            jitter_row = np.random.randint(-3, 4)  # Random offset in range [-3, 3]
            jitter_col = np.random.randint(-3, 4)
            jittered_row = min(max(new_row + jitter_row, 0), desired_rows - 1)
            jittered_col = min(max(new_col + jitter_col, 0), desired_cols - 1)
            
            # Assign a random value between min and max to the new position
            if expanded_matrix[jittered_row, jittered_col] == 0:  # Avoid overwriting
                expanded_matrix[jittered_row, jittered_col] = np.random.uniform(min_value, max_value)
    
    return expanded_matrix

def create_multiple_matrices(file_path, output_directory, desired_rows, desired_cols, desired_density, desired_num):
    # Load the original matrix
    original_matrix = load_matrix(file_path)

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    if original_matrix is not None:
        #print("Original matrix loaded successfully.")
        #print("Shape of original matrix:", original_matrix.shape)
        
        if all(v is not None for v in [desired_rows, desired_cols, desired_density, desired_num]):
            #print(f"Desired dimensions: {desired_rows}x{desired_cols}, Density: {desired_density}, Matrices: {desired_num}")

            for i in range(desired_num):
                # Expand the matrix
                expanded_matrix = expand_matrix(original_matrix, desired_rows, desired_cols, desired_density)

                #display_matrices(original_matrix, expanded_matrix)
                
                # Save the generated matrices in .mtx format
                save_path = f"{output_directory}/expanded_matrix_{i+1}.mtx"
                scipy.io.mmwrite(save_path, csr_matrix(expanded_matrix))
        else:
            print("Failed to get valid dimensions or inputs.")
    else:
        print("Failed to load the matrix.")


def display_matrices(original_matrix, expanded_matrix):
    """Display the original and expanded matrices' sparsity patterns side by side and show non-zero counts."""
    original_nonzeros = np.count_nonzero(original_matrix)
    expanded_nonzeros = np.count_nonzero(expanded_matrix)
    
    #print(f"Number of non-zero elements in the original matrix: {original_nonzeros}")
    #print(f"Number of non-zero elements in the expanded matrix: {expanded_nonzeros}")
    
    plt.figure(figsize=(12, 6))
    
    # Display the sparsity pattern of the original matrix
    plt.subplot(1, 2, 1)
    plt.title(f"Original Matrix\nNon-Zeros: {original_nonzeros}")
    plt.spy(original_matrix, markersize=1)
    
    # Display the sparsity pattern of the expanded matrix
    plt.subplot(1, 2, 2)
    plt.title(f"Expanded Matrix\nNon-Zeros: {expanded_nonzeros}")
    plt.spy(expanded_matrix, markersize=1)
    
    plt.tight_layout()
    plt.show()
import random
import numpy as np
import scipy.io as sio
from scipy import sparse

def scale_sparse_matrix_bilinear(original_matrix: sparse.csr_matrix, new_size: int, output_path: str, match_nnz = True) -> sparse.csr_matrix:
    """
    Scale a sparse matrix with bilinear interpolation while maintaining the sparsity pattern,
    working directly with sparse representation to avoid dense conversion.
    
    Parameters:
    -----------
    original_matrix : scipy.sparse.spmatrix
        Input sparse matrix to be scaled
    new_size : int
        New size for the matrix (will be scaled to new_size x new_size)
    output_path : str
        Output path for saving the scaled matrix as .mtx file
    match_nnz: bool
        To decide match the exact number of nonzeros or not
        
    Returns:
    --------
    scipy.sparse.csr_matrix
        Scaled sparse matrix with preserved value range and linearly scaled number of nonzeros
    """
    # Convert to CSR for efficient row slicing and COO for coordinate access
    original_csr = sparse.csr_matrix(original_matrix)
    original_coo = sparse.coo_matrix(original_matrix)
    
    # Get original dimensions and values
    original_size = max(original_matrix.shape)
    orig_nnz = original_matrix.nnz
    
    # Calculate scaling factor and target nonzeros
    scale_factor = new_size / original_size
    target_nnz = int(orig_nnz * scale_factor)
    
    # Create a dictionary to store new coordinates and values
    new_coords = {}
    
    # Calculate how many points to sample initially
    sample_count = min(int(target_nnz * 1.5), new_size * new_size)
    
    # Generate random coordinates in the new matrix
    candidates = set()
    while len(candidates) < sample_count:
        new_row = random.randint(0, new_size - 1)
        new_col = random.randint(0, new_size - 1)
        candidates.add((new_row, new_col))
    
    # For each sampled coordinate, perform bilinear interpolation
    for new_row, new_col in candidates:
        # Map back to original matrix coordinates
        orig_row_float = new_row / scale_factor
        orig_col_float = new_col / scale_factor
        
        # Get the four surrounding points in the original matrix
        row_low = int(np.floor(orig_row_float))
        row_high = min(row_low + 1, original_size - 1)
        col_low = int(np.floor(orig_col_float))
        col_high = min(col_low + 1, original_size - 1)
        
        # Calculate interpolation weights
        w_row = orig_row_float - row_low
        w_col = orig_col_float - col_low
        
        # Get values from the original matrix without converting to dense
        # This is the key improvement - we access values directly from CSR format
        val_ll = original_csr[row_low, col_low] if row_low < original_size and col_low < original_size else 0
        val_lh = original_csr[row_low, col_high] if row_low < original_size and col_high < original_size else 0
        val_hl = original_csr[row_high, col_low] if row_high < original_size and col_low < original_size else 0
        val_hh = original_csr[row_high, col_high] if row_high < original_size and col_high < original_size else 0
        
        # Perform bilinear interpolation
        top = (1 - w_col) * val_ll + w_col * val_lh
        bottom = (1 - w_col) * val_hl + w_col * val_hh
        value = (1 - w_row) * top + w_row * bottom
        
        # Only add non-zero values to our result
        if abs(value) > 1e-10:  # Small threshold to handle floating point errors
            new_coords[(new_row, new_col)] = value
    
    # Ensure we have exactly target_nnz non-zeros if required
    if match_nnz:
        current_coords = list(new_coords.items())
        current_nnz = len(current_coords)
        
        if current_nnz > target_nnz:
            # Too many non-zeros, randomly remove some
            to_keep = random.sample(current_coords, target_nnz)
            new_coords = dict(to_keep)
        elif current_nnz < target_nnz:
            # Too few non-zeros, we need to add more
            # Get the original values for sampling
            original_values = original_coo.data
            
            # Create an efficient lookup of existing coordinates to avoid duplicates
            existing_coords = set(new_coords.keys())
            
            while len(new_coords) < target_nnz:
                new_row = random.randint(0, new_size - 1)
                new_col = random.randint(0, new_size - 1)
                
                if (new_row, new_col) not in existing_coords:
                    # Map to original matrix for interpolation
                    orig_row_float = new_row / scale_factor
                    orig_col_float = new_col / scale_factor
                    
                    # Get the four surrounding points
                    row_low = int(np.floor(orig_row_float))
                    row_high = min(row_low + 1, original_size - 1)
                    col_low = int(np.floor(orig_col_float))
                    col_high = min(col_low + 1, original_size - 1)
                    
                    # Calculate interpolation weights
                    w_row = orig_row_float - row_low
                    w_col = orig_col_float - col_low
                    
                    # Get values directly from sparse matrix
                    val_ll = original_csr[row_low, col_low]
                    val_lh = original_csr[row_low, col_high]
                    val_hl = original_csr[row_high, col_low]
                    val_hh = original_csr[row_high, col_high]
                    
                    # Perform bilinear interpolation
                    top = (1 - w_col) * val_ll + w_col * val_lh
                    bottom = (1 - w_col) * val_hl + w_col * val_hh
                    value = (1 - w_row) * top + w_row * bottom
                    
                    if abs(value) > 1e-10:
                        new_coords[(new_row, new_col)] = value
                        existing_coords.add((new_row, new_col))
    
    # Convert the dictionary to COO format
    result_rows = []
    result_cols = []
    result_vals = []
    
    for (row, col), val in new_coords.items():
        result_rows.append(row)
        result_cols.append(col)
        result_vals.append(val)
    
    # Create the final sparse matrix and save it to output_path
    scaled_matrix = sparse.csr_matrix((result_vals, (result_rows, result_cols)), shape=(new_size, new_size))
    sio.mmwrite(output_path, scaled_matrix)
    
    return scaled_matrix
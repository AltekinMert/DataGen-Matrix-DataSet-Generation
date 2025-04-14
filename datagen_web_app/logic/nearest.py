import random
import numpy as np
import scipy.io as sio
from scipy import sparse

def scale_sparse_matrix_nearest(original_matrix: sparse.csr_matrix, new_size: int, output_path: str, match_nnz: bool = True) -> sparse.csr_matrix:
    """
    Scale a sparse matrix with nearest-neighbor interpolation while maintaining the sparsity pattern.
    
    Parameters:
    -----------
    original_matrix : scipy.sparse.spmatrix
        Input sparse matrix to be scaled
    new_size : int
        New size for the matrix (will be scaled to new_size x new_size)
    output_path : str
        Output path for saving the scaled matrix as .mtx file
    match_nnz: bool
        To decide match the exact number of nonzeros or not, adjust to exactly match target_nnz if needed
        
    Returns:
    --------
    scipy.sparse.csr_matrix
        Scaled sparse matrix with preserved value range and linearly scaled number of nonzeros
    """
    # Convert to COO format to easily access coordinates and values
    original_matrix = sparse.coo_matrix(original_matrix)
    
    # Get original dimensions
    original_size = max(original_matrix.shape)
    
    # Calculate scaling factor
    scale_factor = new_size / original_size
    
    # Get coordinates and values of nonzeros in the original matrix
    orig_rows = original_matrix.row
    orig_cols = original_matrix.col
    orig_vals = original_matrix.data
    
    # Calculate how many nonzeros we should have in the scaled matrix, linear scaling factor
    orig_nnz = len(orig_vals)
    target_nnz = int(orig_nnz * scale_factor)
    
    # Calculate the size of the neighborhood square
    neighborhood_size = int(scale_factor)
    half_size = max(1, neighborhood_size // 2)
    
    # Determine how many original nonzeros to keep
    # If scale_factor < 1 (downscaling), we'll keep a subset of original nonzeros
    # If scale_factor > 1 (upscaling), we'll keep all original nonzeros and generate new ones
    if scale_factor < 1:
        # Downscaling: randomly select a subset of original nonzeros
        indices_to_keep = np.random.choice(len(orig_rows), size=target_nnz, replace=False)
        base_rows = orig_rows[indices_to_keep]
        base_cols = orig_cols[indices_to_keep]
        base_vals = orig_vals[indices_to_keep]
    else:
        # Upscaling: keep all original nonzeros
        base_rows = orig_rows
        base_cols = orig_cols
        base_vals = orig_vals
    
    # Scale the base coordinates to the new matrix size
    # Nearest-neighbor interpolation
    scaled_rows = np.clip((base_rows * scale_factor).astype(int), 0, new_size - 1)
    scaled_cols = np.clip((base_cols * scale_factor).astype(int), 0, new_size - 1)
    
    # If we're upscaling, add the new nonzeros
    if scale_factor > 1:
        additional_needed = target_nnz - len(base_vals)
        
        if additional_needed > 0:
            # Randomly select some existing nonzeros to generate neighbors for
            indices_for_neighbors = np.random.choice(len(base_vals), size=additional_needed, replace=True)
            
            additional_rows = []
            additional_cols = []
            additional_vals = []
            
            # Generate new nonzeros near selected existing ones
            for idx in indices_for_neighbors:
                base_row = scaled_rows[idx]
                base_col = scaled_cols[idx]
                
                # Generate random offsets within the neighborhood
                row_offset = random.randint(-half_size, half_size)
                col_offset = random.randint(-half_size, half_size)
                
                new_row = min(max(0, base_row + row_offset), new_size - 1)
                new_col = min(max(0, base_col + col_offset), new_size - 1)
                
                # Choose a value from the original matrix
                new_val = random.choice(orig_vals)
                
                additional_rows.append(new_row)
                additional_cols.append(new_col)
                additional_vals.append(new_val)
            
            # Combine base and additional nonzeros
            final_rows = np.concatenate([scaled_rows, additional_rows])
            final_cols = np.concatenate([scaled_cols, additional_cols])
            final_vals = np.concatenate([base_vals, additional_vals])
        else:
            final_rows = scaled_rows
            final_cols = scaled_cols
            final_vals = base_vals
    else:
        # For downscaling, just use the scaled coordinates
        final_rows = scaled_rows
        final_cols = scaled_cols
        final_vals = base_vals
    
    # Handle collisions (50% chance for each value)
    # Create a dictionary to track positions and corresponding values
    position_dict = {}
    for i in range(len(final_rows)):
        pos = (final_rows[i], final_cols[i])
        if pos in position_dict:
            # Collision detected, choose between old and new value with 50% probability
            if random.random() < 0.5:
                position_dict[pos] = final_vals[i]
        else:
            position_dict[pos] = final_vals[i]
    
    # Convert the dictionary back to coordinates and values
    result_rows = []
    result_cols = []
    result_vals = []
    
    for pos, val in position_dict.items():
        result_rows.append(pos[0])
        result_cols.append(pos[1])
        result_vals.append(val)
    
    # If we want to have exact (scale_factor * orig_vals) number of nonzeros
    if match_nnz:
        current_nnz = len(result_rows)
        if current_nnz > target_nnz:
            # Too many nonzeros, randomly remove some
            indices = list(range(current_nnz))
            indices_to_keep = random.sample(indices, target_nnz)
            
            result_rows = [result_rows[i] for i in indices_to_keep]
            result_cols = [result_cols[i] for i in indices_to_keep]
            result_vals = [result_vals[i] for i in indices_to_keep]
        elif current_nnz < target_nnz:
            # Too few nonzeros, add more
            while len(result_rows) < target_nnz:
                # Choose a random existing nonzero to add a neighbor
                idx = random.randint(0, len(result_rows) - 1)
                base_row = result_rows[idx]
                base_col = result_cols[idx]
                
                # Generate a nearby position
                row_offset = random.randint(-half_size, half_size)
                col_offset = random.randint(-half_size, half_size)
                
                new_row = min(max(0, base_row + row_offset), new_size - 1)
                new_col = min(max(0, base_col + col_offset), new_size - 1)
                
                # Check if position is already occupied
                if (new_row, new_col) not in position_dict:
                    position_dict[(new_row, new_col)] = random.choice(orig_vals)
                    result_rows.append(new_row)
                    result_cols.append(new_col)
                    result_vals.append(position_dict[(new_row, new_col)])
    
    # Create the final sparse matrix and save it to output_path
    scaled_matrix = sparse.csr_matrix((result_vals, (result_rows, result_cols)), shape=(new_size, new_size))
    sio.mmwrite(output_path, scaled_matrix)

    return scaled_matrix
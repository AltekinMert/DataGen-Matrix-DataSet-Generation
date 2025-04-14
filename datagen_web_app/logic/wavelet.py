import numpy as np
import scipy.sparse as sp
from scipy.ndimage import zoom
import pywt

def round_to_multiple(n: int, multiple: int) -> int:
    """Round a number to the nearest multiple."""
    return ((n + multiple - 1) // multiple) * multiple

def perturb_details(coeff: np.ndarray) -> np.ndarray:
    """Add random perturbation to detail coefficients."""
    if coeff.size == 0:
        return coeff
    noise = np.random.normal(0, np.std(coeff) * 0.1, coeff.shape)
    return coeff + noise

def scale_sparse_matrix_wavelet(original_matrix: sp.csr_matrix, new_rows: int, new_cols: int) -> sp.csr_matrix:
    """
    Generate a new matrix using wavelet transform and reconstruction.
    Processes the matrix in blocks to handle large sparse matrices efficiently.
    """
    # Ensure dimensions are compatible with wavelet transform
    level = 2  # Reduced from 2 to avoid boundary effects
    block_size = 2**level
    
    # Round dimensions to nearest multiple of block_size
    orig_rows, orig_cols = original_matrix.shape
    padded_rows = round_to_multiple(orig_rows, block_size)
    padded_cols = round_to_multiple(orig_cols, block_size)
    
    # Process matrix in blocks
    block_rows = padded_rows // block_size
    block_cols = padded_cols // block_size
    
    # Initialize result matrix components
    result_data = []
    result_rows = []
    result_cols = []
    
    # Choose wavelet
    wavelet = 'db4'
    
    # Process each block
    for i in range(block_rows):
        for j in range(block_cols):
            # Extract block
            start_row = i * block_size
            start_col = j * block_size
            block = original_matrix[start_row:start_row + block_size, 
                                  start_col:start_col + block_size].toarray()
            
            # Apply wavelet transform
            coeffs = pywt.wavedec2(block, wavelet, level=level)
            cA, (cH, cV, cD) = coeffs
            
            # Calculate scaling factors
            scale_rows = new_rows / orig_rows
            scale_cols = new_cols / orig_cols
            
            # Calculate target size
            target_size = (int(block_size * scale_rows), int(block_size * scale_cols))
            
            # Resize coefficients
            new_cA = zoom(cA, (target_size[0]/cA.shape[0], target_size[1]/cA.shape[1]), order=2)
            new_cH = zoom(cH, (target_size[0]/cH.shape[0], target_size[1]/cH.shape[1]), order=2)
            new_cV = zoom(cV, (target_size[0]/cV.shape[0], target_size[1]/cV.shape[1]), order=2)
            new_cD = zoom(cD, (target_size[0]/cD.shape[0], target_size[1]/cD.shape[1]), order=2)
            
            # Add perturbation to detail coefficients
            new_cH = perturb_details(new_cH)
            new_cV = perturb_details(new_cV)
            new_cD = perturb_details(new_cD)
            
            # Reconstruct block
            new_coeffs = [new_cA, (new_cH, new_cV, new_cD)]
            reconstructed = pywt.waverec2(new_coeffs, wavelet)
            
            # Ensure reconstructed block matches target size
            if reconstructed.shape != target_size:
                reconstructed = zoom(reconstructed, 
                                  (target_size[0]/reconstructed.shape[0], 
                                   target_size[1]/reconstructed.shape[1]), 
                                  order=1)
            
            # Calculate new block position
            new_start_row = int(start_row * scale_rows)
            new_start_col = int(start_col * scale_cols)
            
            # Add non-zero elements to result
            for r in range(min(target_size[0], new_rows - new_start_row)):
                for c in range(min(target_size[1], new_cols - new_start_col)):
                    val = reconstructed[r, c]
                    if abs(val) > 1e-10:  # Threshold for sparsity
                        row_idx = new_start_row + r
                        col_idx = new_start_col + c
                        if row_idx < new_rows and col_idx < new_cols:
                            result_rows.append(row_idx)
                            result_cols.append(col_idx)
                            result_data.append(val)
    
    return sp.csr_matrix((result_data, (result_rows, result_cols)), 
                        shape=(new_rows, new_cols))
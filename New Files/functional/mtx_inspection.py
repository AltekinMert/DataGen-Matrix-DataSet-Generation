import scipy.io
import numpy as np

# Utility function to load matrix

def load_mtx_file(file_path):
    try:
        matrix = scipy.io.mmread(file_path)
        return matrix.toarray() if hasattr(matrix, "toarray") else matrix
    except Exception as e:
        print(f"Error loading .mtx file: {e}")
        return None

# 1. Basic Properties
def get_basic_properties(matrix):
    num_rows, num_cols = matrix.shape
    num_nonzeros = np.count_nonzero(matrix)
    density_percent = 100 * num_nonzeros / (num_rows * num_cols)
    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "num_nonzeros": num_nonzeros,
        "density_percent": density_percent
    }

# 2. Symmetry
def get_symmetry(matrix):
    transpose = matrix.T
    pattern_symmetry = np.array_equal(matrix != 0, transpose != 0)
    numerical_symmetry = np.allclose(matrix, transpose, atol=1e-8)
    return {
        "pattern_symmetry": pattern_symmetry,
        "numerical_symmetry": numerical_symmetry
    }

# 3. Nonzeros per Row
def get_nonzeros_per_row_stats(matrix):
    nonzeros_per_row = np.count_nonzero(matrix, axis=1)
    return {
        "nonzeros_per_row_min": np.min(nonzeros_per_row),
        "nonzeros_per_row_max": np.max(nonzeros_per_row),
        "nonzeros_per_row_avg": np.mean(nonzeros_per_row),
        "nonzeros_per_row_std": np.std(nonzeros_per_row)
    }

# 4. Nonzeros per Column
def get_nonzeros_per_col_stats(matrix):
    nonzeros_per_col = np.count_nonzero(matrix, axis=0)
    return {
        "nonzeros_per_col_min": np.min(nonzeros_per_col),
        "nonzeros_per_col_max": np.max(nonzeros_per_col),
        "nonzeros_per_col_avg": np.mean(nonzeros_per_col),
        "nonzeros_per_col_std": np.std(nonzeros_per_col)
    }

# 5. Nonzero Values Statistics
def get_nonzero_value_stats(matrix):
    nonzero_values = matrix[matrix != 0]
    return {
        "value_min": np.min(nonzero_values),
        "value_max": np.max(nonzero_values),
        "value_avg": np.mean(nonzero_values),
        "value_std": np.std(nonzero_values)
    }

# 6. Row-wise Statistics
def get_row_statistics(matrix):
    row_mins = np.min(matrix, axis=1)
    row_maxs = np.max(matrix, axis=1)
    row_means = np.mean(matrix, axis=1)
    row_stds = np.std(matrix, axis=1)
    row_medians = np.median(matrix, axis=1)
    return {
        "row_min_min": np.min(row_mins),
        "row_min_max": np.max(row_mins),
        "row_min_mean": np.mean(row_mins),
        "row_min_std": np.std(row_mins),

        "row_max_min": np.min(row_maxs),
        "row_max_max": np.max(row_maxs),
        "row_max_mean": np.mean(row_maxs),
        "row_max_std": np.std(row_maxs),

        "row_mean_min": np.min(row_means),
        "row_mean_max": np.max(row_means),
        "row_mean_mean": np.mean(row_means),
        "row_mean_std": np.std(row_means),

        "row_std_min": np.min(row_stds),
        "row_std_max": np.max(row_stds),
        "row_std_mean": np.mean(row_stds),
        "row_std_std": np.std(row_stds),

        "row_median_min": np.min(row_medians),
        "row_median_max": np.max(row_medians),
        "row_median_mean": np.mean(row_medians),
        "row_median_std": np.std(row_medians)
    }

# 7. Column-wise Statistics
def get_col_statistics(matrix):
    col_mins = np.min(matrix, axis=0)
    col_maxs = np.max(matrix, axis=0)
    col_means = np.mean(matrix, axis=0)
    col_stds = np.std(matrix, axis=0)
    col_medians = np.median(matrix, axis=0)
    return {
        "col_min_min": np.min(col_mins),
        "col_min_max": np.max(col_mins),
        "col_min_mean": np.mean(col_mins),
        "col_min_std": np.std(col_mins),

        "col_max_min": np.min(col_maxs),
        "col_max_max": np.max(col_maxs),
        "col_max_mean": np.mean(col_maxs),
        "col_max_std": np.std(col_maxs),

        "col_mean_min": np.min(col_means),
        "col_mean_max": np.max(col_means),
        "col_mean_mean": np.mean(col_means),
        "col_mean_std": np.std(col_means),

        "col_std_min": np.min(col_stds),
        "col_std_max": np.max(col_stds),
        "col_std_mean": np.mean(col_stds),
        "col_std_std": np.std(col_stds),

        "col_median_min": np.min(col_medians),
        "col_median_max": np.max(col_medians),
        "col_median_mean": np.mean(col_medians),
        "col_median_std": np.std(col_medians)
    }

# 8. Distance to Diagonal
def get_distance_to_diagonal(matrix):
    rows, cols = np.nonzero(matrix)
    distances = np.abs(rows - cols)
    avg_distance_to_diagonal = np.mean(distances)
    num_diagonals_with_nonzeros = len(np.unique(distances))
    bandwidth = np.max(distances)
    return {
        "avg_distance_to_diagonal": avg_distance_to_diagonal,
        "num_diagonals_with_nonzeros": num_diagonals_with_nonzeros,
        "bandwidth": bandwidth
    }

# 9. Structural Unsymmetry
def get_structural_unsymmetry(matrix):
    unsymmetric = np.logical_xor(matrix != 0, matrix.T != 0)
    num_structurally_unsymmetric_elements = np.sum(unsymmetric)
    return {"num_structurally_unsymmetric_elements": num_structurally_unsymmetric_elements}

# 10. Norms
def get_matrix_norms(matrix):
    norm_1 = np.linalg.norm(matrix, ord=1)
    norm_inf = np.linalg.norm(matrix, ord=np.inf)
    frobenius_norm = np.linalg.norm(matrix, ord='fro')
    return {
        "norm_1": norm_1,
        "norm_inf": norm_inf,
        "frobenius_norm": frobenius_norm
    }

# 11. Condition Number
def get_condition_number(matrix):
    try:
        condition_number = np.linalg.cond(matrix, p=1)
    except np.linalg.LinAlgError:
        condition_number = float('inf')  # Handle singular matrices
    return {"estimated_condition_number": condition_number}
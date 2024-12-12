import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as splinalg

def compute_features(matrix):
    features = {}

    # Basic properties
    rows, cols = matrix.shape
    nnz = matrix.nnz
    density = nnz / (rows * cols) * 100 

    features['num_rows'] = rows
    features['num_cols'] = cols
    features['num_nonzeros'] = nnz
    features['density_percent'] = density

    # Symmetry
    if rows == cols:
        is_pattern_symmetric = (matrix != matrix.T).nnz == 0
        is_numerical_symmetric = (matrix - matrix.T).nnz == 0
    else:
        is_pattern_symmetric = False
        is_numerical_symmetric = False

    features['pattern_symmetry'] = is_pattern_symmetric
    features['numerical_symmetry'] = is_numerical_symmetric

    # Nonzeros per row
    nonzeros_per_row = matrix.getnnz(axis=1)
    features['nonzeros_per_row_min'] = np.min(nonzeros_per_row)
    features['nonzeros_per_row_max'] = np.max(nonzeros_per_row)
    features['nonzeros_per_row_avg'] = np.mean(nonzeros_per_row)
    features['nonzeros_per_row_std'] = np.std(nonzeros_per_row)

    # Nonzeros per column
    nonzeros_per_col = matrix.getnnz(axis=0)
    features['nonzeros_per_col_min'] = np.min(nonzeros_per_col)
    features['nonzeros_per_col_max'] = np.max(nonzeros_per_col)
    features['nonzeros_per_col_avg'] = np.mean(nonzeros_per_col)
    features['nonzeros_per_col_std'] = np.std(nonzeros_per_col)

    # Non-zero values statistics
    data = matrix.data
    features['value_min'] = data.min()
    features['value_max'] = data.max()
    features['value_avg'] = data.mean()
    features['value_std'] = data.std()

    # Per-row statistics
    csr_matrix = matrix.tocsr()
    row_min = np.zeros(rows)
    row_max = np.zeros(rows)
    row_mean = np.zeros(rows)
    row_std = np.zeros(rows)
    row_median = np.zeros(rows)

    for i in range(rows):
        row_data = csr_matrix.data[csr_matrix.indptr[i]:csr_matrix.indptr[i+1]]
        if len(row_data) > 0:
            row_min[i] = row_data.min()
            row_max[i] = row_data.max()
            row_mean[i] = row_data.mean()
            row_std[i] = row_data.std()
            row_median[i] = np.median(row_data)
        else:
            # Handle empty rows
            row_min[i] = 0
            row_max[i] = 0
            row_mean[i] = 0
            row_std[i] = 0
            row_median[i] = 0

    # Summarize per-row statistics
    features['row_min_min'] = row_min.min()
    features['row_min_max'] = row_min.max()
    features['row_min_mean'] = row_min.mean()
    features['row_min_std'] = row_min.std()

    features['row_max_min'] = row_max.min()
    features['row_max_max'] = row_max.max()
    features['row_max_mean'] = row_max.mean()
    features['row_max_std'] = row_max.std()

    features['row_mean_min'] = row_mean.min()
    features['row_mean_max'] = row_mean.max()
    features['row_mean_mean'] = row_mean.mean()
    features['row_mean_std'] = row_mean.std()

    features['row_std_min'] = row_std.min()
    features['row_std_max'] = row_std.max()
    features['row_std_mean'] = row_std.mean()
    features['row_std_std'] = row_std.std()

    features['row_median_min'] = row_median.min()
    features['row_median_max'] = row_median.max()
    features['row_median_mean'] = row_median.mean()
    features['row_median_std'] = row_median.std()

    # Per-column statistics
    csc_matrix = matrix.tocsc()
    col_min = np.zeros(cols)
    col_max = np.zeros(cols)
    col_mean = np.zeros(cols)
    col_std = np.zeros(cols)
    col_median = np.zeros(cols)

    for j in range(cols):
        col_data = csc_matrix.data[csc_matrix.indptr[j]:csc_matrix.indptr[j+1]]
        if len(col_data) > 0:
            col_min[j] = col_data.min()
            col_max[j] = col_data.max()
            col_mean[j] = col_data.mean()
            col_std[j] = col_data.std()
            col_median[j] = np.median(col_data)
        else:
            # Handle empty columns
            col_min[j] = 0
            col_max[j] = 0
            col_mean[j] = 0
            col_std[j] = 0
            col_median[j] = 0

    # Summarize per-column statistics
    features['col_min_min'] = col_min.min()
    features['col_min_max'] = col_min.max()
    features['col_min_mean'] = col_min.mean()
    features['col_min_std'] = col_min.std()

    features['col_max_min'] = col_max.min()
    features['col_max_max'] = col_max.max()
    features['col_max_mean'] = col_max.mean()
    features['col_max_std'] = col_max.std()

    features['col_mean_min'] = col_mean.min()
    features['col_mean_max'] = col_mean.max()
    features['col_mean_mean'] = col_mean.mean()
    features['col_mean_std'] = col_mean.std()

    features['col_std_min'] = col_std.min()
    features['col_std_max'] = col_std.max()
    features['col_std_mean'] = col_std.mean()
    features['col_std_std'] = col_std.std()

    features['col_median_min'] = col_median.min()
    features['col_median_max'] = col_median.max()
    features['col_median_mean'] = col_median.mean()
    features['col_median_std'] = col_median.std()

    # Average distance of nonzero elements to the diagonal
    row_indices, col_indices = matrix.nonzero()
    distances = np.abs(row_indices - col_indices)
    avg_distance = distances.mean()
    features['avg_distance_to_diagonal'] = avg_distance

    # Number of diagonals that have non-zero elements
    unique_distances = np.unique(distances)
    num_diagonals_with_nonzeros = len(unique_distances)
    features['num_diagonals_with_nonzeros'] = num_diagonals_with_nonzeros

    # Bandwidth
    bandwidth = distances.max()
    features['bandwidth'] = bandwidth

    # Number of structurally unsymmetric elements
    nonzero_positions = set(zip(row_indices, col_indices))
    nonzero_positions_T = set(zip(col_indices, row_indices))
    unsymmetric_elements = nonzero_positions - nonzero_positions_T
    num_unsymmetric_elements = len(unsymmetric_elements)
    features['num_structurally_unsymmetric_elements'] = num_unsymmetric_elements

    # Norms
    features['norm_1'] = splinalg.norm(matrix, 1)
    features['norm_inf'] = splinalg.norm(matrix, np.inf)
    features['frobenius_norm'] = splinalg.norm(matrix)

    # Estimated condition number (1-norm)
    try:
        cond_est = splinalg.onenormest(matrix)
        features['estimated_condition_number'] = cond_est
    except:
        features['estimated_condition_number'] = None

    return features


def compute_average_features(features_list):
    # Compute average of numeric features
    average_features = {}
    keys = features_list[0].keys()
    for key in keys:
        if isinstance(features_list[0][key], (int, float, np.number)):
            average_features[key] = np.mean([feat[key] for feat in features_list])
        else:
            average_features[key] = features_list[0][key]
    return average_features
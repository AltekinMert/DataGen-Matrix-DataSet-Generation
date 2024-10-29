import numpy as np
import scipy.sparse as sp

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
    else:
        is_pattern_symmetric = False

    features['pattern_symmetry'] = is_pattern_symmetric

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

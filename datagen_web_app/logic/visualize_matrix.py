import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def visualize_matrices(matrix1, matrix2, title1="Original Matrix", title2="Expanded Matrix", save_path=None):
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    scale_factor = matrix2.shape[0] / matrix1.shape[0]

    values1 = matrix1.data
    values2 = matrix2.data

    min_val1, max_val1 = np.min(values1), np.max(values1) if values1.size > 0 else (0, 0)
    min_val2, max_val2 = np.min(values2), np.max(values2) if values2.size > 0 else (0, 0)

    axes[0].spy(matrix1, markersize=1)
    axes[0].set_title(title1, fontsize=14)
    axes[0].set_xlabel(f"Nonzeros: {matrix1.nnz}\nMin: {min_val1:.2f}, Max: {max_val1:.2f}", fontsize=12)

    axes[1].spy(matrix2, markersize=1)
    axes[1].set_title(title2, fontsize=14)
    axes[1].set_xlabel(f"Nonzeros: {matrix2.nnz}\nMin: {min_val2:.2f}, Max: {max_val2:.2f}", fontsize=12)

    fig.suptitle(f"Expansion Factor: {scale_factor:.2f}", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
    plt.close()
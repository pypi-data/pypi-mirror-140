"""Utility functions for attitude dynamics."""

import numpy as np


def cross_matrix(vector) -> np.ndarray:
    """The cross-product 'tilde' matrix of a 3x1 vector."""
    return np.array(
        [
            [0, -vector[2], vector[1]],
            [vector[2], 0, -vector[0]],
            [-vector[1], vector[0], 0]
        ]
    )

"""One-time script to generate pre-processed Y2 cubes for the H2BO demo.

This script reads the original MATLAB data files (fractional abundances
and spectral library) and reproduces the synthetic observation process
from ``demo_H2BO.m``, saving each result as ``data/<dataset>_Y2.mat``.

Usage
-----
    python scripts/prepare_demo_cubes.py [--data <path>]

The ``--data`` flag defaults to this branch's ``data`` directory.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import scipy.io as sio
from scipy.fft import dct, idct


def _prune_library(A: np.ndarray, min_angle: float):
    """Remove columns so the minimum angle between any two is at least *min_angle*.

    Translated from ``prune_library2.m``.
    """
    L, m = A.shape
    nA = np.sqrt(np.sum(A ** 2, axis=0))
    A_norm = A / nA[np.newaxis, :]

    # Compute pairwise angles in degrees
    cos_vals = np.clip(A_norm.T @ A_norm, -1, 1)
    angles = np.abs(np.arccos(cos_vals)) * 180 / np.pi

    index_kept = []
    for i in range(m):
        if angles[i, i] != np.inf:
            index_kept.append(i)
            discard = angles[i, :] < min_angle
            angles[:, discard] = np.inf

    B = A[:, index_kept]
    return B, np.array(index_kept)


def _sort_library_by_angle(A: np.ndarray):
    """Sort columns of *A* by increasing minimum angle to any other column.

    Translated from ``sort_library_by_angle.m``.
    """
    BIG = 1e10
    L, m = A.shape
    nA = np.sqrt(np.sum(A ** 2, axis=0))
    A_norm = A / nA[np.newaxis, :]

    cos_vals = np.clip(A_norm.T @ A_norm, -1, 1)
    angles = np.abs(np.arccos(cos_vals)) * 180 / np.pi
    angles += BIG * np.eye(m)

    min_angles = angles.min(axis=0)
    index = np.argsort(min_angles)
    sorted_angles = min_angles[index]

    B = A[:, index]
    return B, index, sorted_angles


def generate_cube(
    data_path: str,
    dataset: str,
    seed: int = 10,
    snr: float = 30,
) -> np.ndarray:
    """Generate the Y2 hyperspectral cube for one dataset.

    Parameters
    ----------
    data_path : str
        Directory containing the MATLAB ``.mat`` files.
    dataset : str
        One of ``"DC1"``, ``"DC2"``, ``"DC3"``.
    seed : int
        Random seed (matches MATLAB ``rand('state', 10)``).
    snr : float
        Signal-to-noise ratio in dB.

    Returns
    -------
    np.ndarray
        The processed cube ``Y2`` with shape ``(rows, cols, bands)``.
    """
    # Load fractional abundances
    mat_dc = sio.loadmat(os.path.join(data_path, f"{dataset}.mat"))
    Xim = mat_dc["Xim"]  # (nl, nc, p)
    nl, nc, p = Xim.shape
    N = nl * nc
    X = mat_dc["X"]  # (p, N)

    # Load spectral library
    mat_lib = sio.loadmat(os.path.join(data_path, "USGS_1995_Library.mat"))
    datalib = mat_lib["datalib"]  # (bands_raw, cols)

    # Sort by wavelength
    wavelength = datalib[:, 0]
    sort_idx = np.argsort(wavelength)
    A = datalib[sort_idx, 3:]  # columns 4:end in MATLAB (0-based col 3:)

    # Prune library
    min_angle = 4.44
    A, kept_idx = _prune_library(A, min_angle)

    # Sort by angle
    A, sort_idx_angle, _ = _sort_library_by_angle(A)

    # Select p endmembers (MATLAB: supp = 2:p+1; Python 0-based: 1:p+1)
    supp = list(range(1, p + 1))
    M = A[:, supp]
    L, p = M.shape

    # Set random state
    rng = np.random.RandomState(seed)

    # Noise standard deviation
    MX = M @ X  # (L, N)
    sigma = np.sqrt(np.sum(MX ** 2) / N / L / 10 ** (snr / 10))

    # Gaussian iid noise
    noise = sigma * rng.randn(L, N)

    # Correlated noise via DCT/IDCT low-pass filter
    bandwidth = 10000
    filter_coef = np.exp(-(np.arange(L) ** 2) / (2 * bandwidth ** 2))
    scale = np.sqrt(L / np.sum(filter_coef ** 2))
    filter_coef = scale * filter_coef

    # Apply filter in DCT domain
    noise_dct = dct(noise, type=2, axis=0, norm=None)
    noise_filtered = idct(
        noise_dct * filter_coef[:, np.newaxis], type=2, axis=0, norm=None
    )
    # scipy dct/idct use a different normalisation than MATLAB;
    # MATLAB dct is unitary, scipy type-2 is unnormalised.
    # Use orthonormal mode instead:
    noise_dct = dct(noise, type=2, axis=0, norm="ortho")
    noise_filtered = idct(
        noise_dct * filter_coef[:, np.newaxis], type=2, axis=0, norm="ortho"
    )

    # Observed data
    Y = MX + noise_filtered  # (L, N)

    # Match MATLAB: Y2 = reshape(Y', nl, nc, L).
    # MATLAB reshape uses column-major order, and X is vectorized from Xim
    # with rows varying fastest. Using NumPy's default row-major reshape here
    # transposes the spatial layout of the generated cubes.
    Y2 = Y.T.reshape(nl, nc, L, order="F")  # (nl, nc, L)

    # Rescale by mean spectral norm
    norms = np.sqrt(np.sum(Y2 ** 2, axis=2))  # (nl, nc)
    scfact = np.mean(norms)
    Y2 = Y2 / scfact

    return Y2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate pre-processed Y2 cubes for the H2BO Python demo.",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to the data directory containing the original .mat files.",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    if args.data:
        matlab_data = args.data
    else:
        matlab_data = os.path.join(project_dir, "data")

    matlab_data = os.path.abspath(matlab_data)
    print(f"MATLAB data directory: {matlab_data}")

    out_dir = os.path.join(project_dir, "data")
    os.makedirs(out_dir, exist_ok=True)

    for ds in ("DC1", "DC2", "DC3"):
        print(f"Generating {ds}_Y2 ...")
        Y2 = generate_cube(matlab_data, ds)
        out_path = os.path.join(out_dir, f"{ds}_Y2.mat")
        sio.savemat(out_path, {"Y2": Y2})
        print(f"  -> Saved {out_path}  shape={Y2.shape}")

    print("Done.")


if __name__ == "__main__":
    main()

"""H2BO - Hierarchical Homogeneity-Based Oversegmentation.

Python port of the MATLAB H2BO algorithm.

Reference
---------
Hierarchical Homogeneity-Based Superpixel Segmentation: Application to
Hyperspectral Image Analysis.
L. C. Ayres, S.J.M. de Almeida, J.C.M. Bermudez, R.A. Borsoi.
International Journal of Remote Sensing, 2024.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import scipy.io as sio

from utils.heter_segments import _run_slic, heter_segments
from utils.homog_median_dist import homog_median_dist
from utils.show_segments import DEFAULT_BANDS, show_segments


DEFAULT_SLIC_SIZE = (8, 7, 4, 3)
DEFAULT_CLI_SLIC_SIZE = (8,)
DEFAULT_SLIC_REG = 5.0
DEFAULT_TAU_OUTLIERS = 10.0
DEFAULT_TAU_HOMOG = 20.0
DEFAULT_GRID_SIZES = (15, 12, 8, 6)
DEFAULT_GRID_REGS = (0.5, 1.0, 2.0, 5.0)
DATASETS = ("DC1", "DC2", "DC3")


def _normalize_slic_size(slic_size: int | Sequence[int]) -> tuple[int, ...]:
    """Return *slic_size* as a validated tuple of positive integers."""
    if isinstance(slic_size, (int, np.integer)):
        sizes = (int(slic_size),)
    else:
        sizes = tuple(int(size) for size in slic_size)

    if not sizes:
        raise ValueError("slic_size must contain at least one region size.")
    if any(size <= 0 for size in sizes):
        raise ValueError("all slic_size values must be positive integers.")
    return sizes


def h2bo(
    data: np.ndarray,
    slic_size: int | Sequence[int] = DEFAULT_SLIC_SIZE,
    slic_reg: float = DEFAULT_SLIC_REG,
    tau_outliers: float = DEFAULT_TAU_OUTLIERS,
    tau_homog: float = DEFAULT_TAU_HOMOG,
    verbose: bool = False,
    return_info: bool = False,
):
    """Run the H2BO hierarchical superpixel segmentation.

    Parameters
    ----------
    data : np.ndarray
        Hyperspectral cube with shape ``(rows, cols, bands)``.
    slic_size : int or sequence of int, optional
        Region sizes for each hierarchical scale. A single integer runs
        only the initial SLIC scale. Multiple values run hierarchical
        refinement, where subsequent entries are used for resegmenting
        heterogeneous superpixels.
    slic_reg : float, optional
        SLIC compactness / regularisation parameter.
    tau_outliers : float, optional
        Percentage of top distances to trim in the homogeneity test.
    tau_homog : float, optional
        Distance-ratio threshold for classifying superpixels.
    verbose : bool, optional
        If ``True``, print per-round statistics.
    return_info : bool, optional
        If ``True``, return a dict of per-round metadata alongside the
        label map.

    Returns
    -------
    sppx : np.ndarray
        2-D integer label map ``(rows, cols)``.
    info : dict
        Only returned when *return_info* is ``True``. Contains lists
        keyed by ``"n_superpixels"``, ``"n_heter"``, ``"n_homog"``,
        and a final ``"homog_percent"`` scalar.
    """
    slic_size = _normalize_slic_size(slic_size)
    data = np.asarray(data)
    if data.ndim != 3:
        raise ValueError("data must have shape (rows, cols, bands).")

    R = len(slic_size) - 1
    info: dict = {
        "n_superpixels": [],
        "n_heter": [],
        "n_homog": [],
        "homog_percent": 0.0,
    }

    if verbose:
        print("r = 0")
    sp_segs = _run_slic(data, slic_size[0], slic_reg)
    labels = np.unique(sp_segs)

    labels_homog, labels_heter, _ = homog_median_dist(
        data,
        sp_segs,
        labels,
        tau_homog,
        tau_outliers,
        verbose=verbose,
    )

    info["n_superpixels"].append(len(labels))
    info["n_heter"].append(len(labels_heter))
    info["n_homog"].append(len(labels_homog))

    for r in range(1, R + 1):
        if verbose:
            print(f"r = {r}")
        if len(labels_heter) == 0:
            if verbose:
                print(f"There are no heterogeneous superpixels in scale r = {r}.")
            break

        prev_max = int(np.max(labels))
        sp_segs, labels_new, _ = heter_segments(
            data,
            sp_segs,
            labels_heter,
            slic_size[r],
            slic_reg,
        )

        labels = labels_new[labels_new > prev_max]
        labels_homog, labels_heter, _ = homog_median_dist(
            data,
            sp_segs,
            labels,
            tau_homog,
            tau_outliers,
            verbose=verbose,
        )

        info["n_superpixels"].append(len(labels_new))
        info["n_heter"].append(len(labels_heter))
        info["n_homog"].append(len(labels_homog))

    all_labels = np.unique(sp_segs)
    labels_homog, _, _ = homog_median_dist(
        data,
        sp_segs,
        all_labels,
        tau_homog,
        tau_outliers,
    )
    if len(all_labels) > 0:
        info["homog_percent"] = 100.0 * len(labels_homog) / len(all_labels)

    if return_info:
        return sp_segs, info
    return sp_segs


def _project_dir() -> Path:
    return Path(__file__).resolve().parent


def _float_tag(value: float) -> str:
    return f"{value:g}".replace("-", "m").replace(".", "p")


def _load_cube(dataset: str, data_dir: Path) -> np.ndarray:
    cube_path = data_dir / f"{dataset}_Y2.mat"
    if not cube_path.exists():
        raise FileNotFoundError(f"Could not find cube file: {cube_path}")

    mat = sio.loadmat(cube_path)
    if "Y2" not in mat:
        raise KeyError(f"{cube_path} does not contain variable 'Y2'.")
    return np.asarray(mat["Y2"])


def _save_segmentation_pdf(
    data: np.ndarray,
    segments: np.ndarray,
    output_path: Path,
    title: str,
    bands: Sequence[int],
) -> None:
    import matplotlib.pyplot as plt

    marked = show_segments(data, segments, bands=tuple(bands))
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(marked)
    ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout(pad=0.1)
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def _run_single(args: argparse.Namespace) -> None:
    dataset = args.dataset or "DC2"
    sizes = _normalize_slic_size(args.slic_size)
    data = _load_cube(dataset, args.data_dir)

    print(f"Dataset: {dataset}")
    print(f"Cube shape: {data.shape}")
    print(f"slic_size: {sizes}")
    print(f"slic_reg: {args.slic_reg:g}")
    print("Computing superpixels ...")

    start = time.perf_counter()
    segments, info = h2bo(
        data,
        slic_size=sizes,
        slic_reg=args.slic_reg,
        tau_outliers=args.tau_outliers,
        tau_homog=args.tau_homog,
        verbose=args.verbose,
        return_info=True,
    )
    elapsed = time.perf_counter() - start

    labels = np.unique(segments)
    print("")
    print("Final oversegmentation:")
    print(f"num_sppx      = {len(labels)}")
    print(f"homog_sppx(%) = {info['homog_percent']:.1f} %")
    print(f"exec_time     = {elapsed:.2f} s")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sio.savemat(args.output_dir / "sppx.mat", {"sppx": segments})

    size_tag = "-".join(str(size) for size in sizes)
    title = f"{dataset} | size={size_tag} | reg={args.slic_reg:g}"
    pdf_path = args.output_dir / "sppx.pdf"
    _save_segmentation_pdf(data, segments, pdf_path, title, args.bands)

    print(f"Saved segmentation -> {args.output_dir / 'sppx.mat'}")
    print(f"Saved figure       -> {pdf_path}")


def _run_grid(args: argparse.Namespace) -> None:
    import matplotlib.pyplot as plt

    dataset = args.dataset or "DC1"
    sizes = tuple(args.grid_sizes)
    regs = tuple(args.grid_regs)
    data = _load_cube(dataset, args.data_dir)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = len(sizes)
    cols = len(regs)
    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(3.1 * cols, 3.35 * rows),
        squeeze=False,
    )

    print(f"Dataset: {dataset}")
    print(f"Cube shape: {data.shape}")
    print(f"grid sizes: {sizes}")
    print(f"grid regs: {regs}")

    for row, size in enumerate(sizes):
        for col, reg in enumerate(regs):
            print(f"Grid cell size={size}, reg={reg:g} ...")
            segments, info = h2bo(
                data,
                slic_size=(size,),
                slic_reg=reg,
                tau_outliers=args.tau_outliers,
                tau_homog=args.tau_homog,
                verbose=False,
                return_info=True,
            )
            marked = show_segments(data, segments, bands=tuple(args.bands))
            n_labels = len(np.unique(segments))

            ax = axes[row, col]
            ax.imshow(marked)
            ax.set_axis_off()
            ax.set_title(
                f"size={size}, reg={reg:g}\n"
                f"sp={n_labels}, homog={info['homog_percent']:.1f}%",
                fontsize=9,
            )

    fig.suptitle(f"{dataset} SLIC Parameter Grid - Single Scale", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.985), pad=0.2)

    regs_tag = "_".join(_float_tag(reg) for reg in regs)
    sizes_tag = "-".join(str(size) for size in sizes)
    pdf_path = args.output_dir / f"grid_{dataset}_sizes_{sizes_tag}_regs_{regs_tag}.pdf"
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"Saved grid figure -> {pdf_path}")


def build_arg_parser() -> argparse.ArgumentParser:
    project_dir = _project_dir()

    parser = argparse.ArgumentParser(
        description="Run H2BO segmentation or generate a SLIC tuning grid.",
    )
    parser.add_argument(
        "--dataset",
        choices=DATASETS,
        default=None,
        help="Dataset to load. Defaults to DC1 for --grid, otherwise DC2.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=project_dir / "data",
        help="Directory containing *_Y2.mat files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_dir / "output",
        help="Directory for output .mat and .pdf files.",
    )
    parser.add_argument(
        "--slic-size",
        type=int,
        nargs="+",
        default=list(DEFAULT_CLI_SLIC_SIZE),
        help=(
            "One or more SLIC region sizes. One value runs a single scale; "
            "multiple values run hierarchical refinement."
        ),
    )
    parser.add_argument(
        "--slic-reg",
        type=float,
        default=DEFAULT_SLIC_REG,
        help="SLIC compactness / regularisation parameter.",
    )
    parser.add_argument(
        "--tau-outliers",
        type=float,
        default=DEFAULT_TAU_OUTLIERS,
        help="Percentage of top distances to trim in the homogeneity test.",
    )
    parser.add_argument(
        "--tau-homog",
        type=float,
        default=DEFAULT_TAU_HOMOG,
        help="Distance-ratio threshold for homogeneous superpixels.",
    )
    parser.add_argument(
        "--bands",
        type=int,
        nargs=3,
        default=list(DEFAULT_BANDS),
        metavar=("R", "G", "B"),
        help="Zero-based band indices for false-colour output.",
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Generate a DC1 single-scale SLIC size/reg comparison grid.",
    )
    parser.add_argument(
        "--grid-sizes",
        type=int,
        nargs="+",
        default=list(DEFAULT_GRID_SIZES),
        help="Region sizes used by --grid.",
    )
    parser.add_argument(
        "--grid-regs",
        type=float,
        nargs="+",
        default=list(DEFAULT_GRID_REGS),
        help="SLIC regularisation values used by --grid.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-round H2BO statistics.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    args.data_dir = args.data_dir.expanduser().resolve()
    args.output_dir = args.output_dir.expanduser().resolve()

    if args.grid:
        _run_grid(args)
    else:
        _run_single(args)


if __name__ == "__main__":
    main()

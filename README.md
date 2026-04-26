# Hierarchical Homogeneity-Based Oversegmentation (H2BO) - Python Port

This branch contains the Python port of the H2BO MATLAB implementation from the `main` branch of this repository.

The `main` branch is preserved as the MATLAB implementation associated with the published paper. Use this branch when you want to run H2BO with Python tooling and `scikit-image`.

If you use this software, please cite:

    [1] Ayres, L. C., de Almeida, S. J. M., Bermudez, J. C. M., & Borsoi, R. A. (2024).
    Hierarchical homogeneity-based superpixel segmentation: application to hyperspectral image analysis.
    International Journal of Remote Sensing, 45(17), 6004-6042.
    https://doi.org/10.1080/01431161.2024.2384098

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare demo cubes

```bash
python scripts/prepare_demo_cubes.py
```

This reads the original MATLAB demo inputs from `data/` and generates:

- `data/DC1_Y2.mat`
- `data/DC2_Y2.mat`
- `data/DC3_Y2.mat`

These generated cubes are ignored by git. They can be regenerated at any time from the original data files kept in this branch.

### 3. Run one segmentation

```bash
python h2bo.py --dataset DC2 --slic-size 8 --slic-reg 5
```

Outputs are saved to `output/sppx.mat` and `output/sppx.pdf`. Figures are written as tight-layout PDFs.

### 4. Run hierarchical segmentation

```bash
python h2bo.py --dataset DC1 --slic-size 30 20 12 8 4 --slic-reg 0.5
```

### 5. Generate a parameter grid

```bash
python h2bo.py --grid
```

The default grid compares single-scale SLIC sizes `15`, `12`, `8`, and `6` against Python/skimage compactness values `0.5`, `1`, `2`, and `5`.

## CLI

```bash
python h2bo.py --help
```

Useful options:

- `--dataset DC1|DC2|DC3`: dataset to load.
- `--slic-size 8`: run one SLIC scale.
- `--slic-size 8 7 4 3`: run hierarchical refinement.
- `--slic-reg 5`: set the skimage SLIC compactness parameter.
- `--tau-outliers 10`: set outlier trimming percentage.
- `--tau-homog 20`: set the homogeneity threshold.
- `--bands 36 15 9`: set zero-based false-colour display bands.
- `--grid`: create a DC1 single-scale size/compactness tuning grid.

`demo_h2bo.py` is kept as a compatibility wrapper and forwards to the same CLI.

## Python API

```python
from h2bo import h2bo

sppx = h2bo(data)                          # returns a 2-D label map
sppx, info = h2bo(data, return_info=True)  # also returns metadata
sppx = h2bo(data, slic_size=8)             # one scale
```

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `np.ndarray` | - | Hyperspectral cube `(rows, cols, bands)` |
| `slic_size` | `int` or `Sequence[int]` | `(8, 7, 4, 3)` | Region sizes per scale |
| `slic_reg` | `float` | `5.0` | skimage SLIC compactness |
| `tau_outliers` | `float` | `10` | Percentage of outlier distances to trim |
| `tau_homog` | `float` | `20` | Homogeneity ratio threshold |
| `verbose` | `bool` | `False` | Print per-round statistics |
| `return_info` | `bool` | `False` | Return metadata dict |

## Project Structure

```text
H2BO/
|-- h2bo.py
|-- demo_h2bo.py
|-- requirements.txt
|-- README.md
|-- reference_paper.pdf
|-- data/
|   |-- DC1.mat
|   |-- DC2.mat
|   |-- DC3.mat
|   `-- USGS_1995_Library.mat
|-- scripts/
|   `-- prepare_demo_cubes.py
|-- tests/
`-- utils/
```

## Differences From The MATLAB Main Branch

- This branch uses `skimage.segmentation.slic` instead of VLFeat `vl_slic`.
- The Python `slic_reg` argument maps to skimage compactness, not directly to the VLFeat regularizer.
- On DC1, MATLAB/VLFeat `slic_reg=0.00225` gives matching single-scale label counts with Python/skimage compactness around `1` to `5`; the default `5` matched the tested sizes `15`, `12`, `8`, and `6`.
- Demo cubes are generated with MATLAB-compatible column-major spatial order (`order="F"`) to preserve the orientation of the original MATLAB data.
- Segment boundary figures use single-pixel contours and are saved as PDF.
- Exact pixel-level parity with MATLAB/VLFeat is not expected.
- Downstream unmixing and classification workflows are not included.

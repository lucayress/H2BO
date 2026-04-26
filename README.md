# Hierarchical Homogeneity-Based Oversegmentation (H2BO)

This is the authors' implementation of the paper [1]. If you use this software please cite the following in any resulting publication:

    [1] Ayres, L. C., de Almeida, S. J. M., Bermudez, J. C. M., & Borsoi, R. A. (2024). 
	Hierarchical homogeneity-based superpixel segmentation: application to hyperspectral image analysis. 
	International Journal of Remote Sensing, 45(17), 6004–6042. 
	https://doi.org/10.1080/01431161.2024.2384098

The algorithm is implemented in MATLAB R2022a and includes the main files and directories:
-  H2BO.m		- function that performs H2BO segmentation on hyperspectral data.
-  demo_H2BO.m	- presents a demonstration of the use of the H2BO function.
-  ./data/ 		- contains the DC1, DC2 and DC3 datasets.
-  ./output/ 	- contains the exported files.
-  ./utils/ 	- contains auxiliary functions.       
It also includes code associated to the paper [2].

## INSTALLING & RUNNING:
* Download the latest version of the VLFeat toolbox at http://www.vlfeat.org/install-matlab.html.
* Start MATLAB and run the script `demo_H2BO.m`.

## PYTHON VERSION:
* A Python port of this implementation is available on the `python` branch of this repository. The `main` branch remains the MATLAB implementation associated with the published paper.

## NOTES:
* The unmixing and classification tasks can be performed, just like in the original study, using the superpixels produced via H2BO or another over/segmentation approach. The MUA [2] algorithm from R. Borsoi was used in the unmixing experiments, and the CEGCN [3] implemetation by Q. Liu was employed in the classification simulations.

* Other public hyperspectral datasets such as Cuprite, Indian Pines, and Salinas are available on the [UPV/EHU](http://www.ehu.eus/ccwintco/index.php?title=Hyperspectral_Remote_Sensing_Scenes) wiki.

## REFERENCES:

[2] A Fast Multiscale Spatial Regularization for Sparse Hyperspectral Unmixing.
R.A. Borsoi, T. Imbiriba, J.C.M. Bermudez, C. Richard.
IEEE Geoscience and Remote Sensing Letters, 2018.
https://github.com/ricardoborsoi/MUA_SparseUnmixing
		
[3] CNN-Enhanced Graph Convolutional Network with Pixel- and Superpixel-Level Feature Fusion for Hyperspectral Image Classification.
Q. Liu, L. Xiao, J. Yang and Z. Wei.
IEEE Transactions on Geoscience and Remote Sensing, 2019.
https://github.com/qichaoliu/CNN_Enhanced_GCN 
 

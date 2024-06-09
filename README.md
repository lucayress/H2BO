# Hierarchical Homogeneity-Based Oversegmentation (H2BO)

This is the authors' implementation of the manuscript [1] in reviewing process. If you use this software please cite the following in any resulting publication:

    [1] Hierarchical Homogeneity-Based Superpixel Segmentation: Application to Hyperspectral Image Analysis
        L. C. Ayres, S.J.M. de Almeida, J.C.M. Bermudez, R.A. Borsoi.
        International Journal of Remote Sensing, 2024.

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

## NOTES:
	* The unmixing and classification tasks can be completed, just like in the original study, using the superpixels produced via H2BO or another segmentation approach. The MUA [2] algorithm from R. Borsoi was used for the unmixing experiments, and the CEGCN [3] implemetation by Q. Liu was employed in the classification simulations.

	* Other public hyperspectral datasets such as Cuprite, Indian Pines, and Salinas are available on the [UPV/EHU](http://www.ehu.eus/ccwintco/index.php?title=Hyperspectral_Remote_Sensing_Scenes) wiki.

## References:

	[2] A Fast Multiscale Spatial Regularization for Sparse Hyperspectral Unmixing.
        R.A. Borsoi, T. Imbiriba, J.C.M. Bermudez, C. Richard.
        IEEE Geoscience and Remote Sensing Letters, 2018.
		https://github.com/ricardoborsoi/MUA_SparseUnmixing
		
	[3] CNN-Enhanced Graph Convolutional Network with Pixel- and Superpixel-Level Feature Fusion for Hyperspectral Image Classification.
		Q. Liu, L. Xiao, J. Yang and Z. Wei.
		IEEE Transactions on Geoscience and Remote Sensing, 2019.
		https://github.com/qichaoliu/CNN_Enhanced_GCN 
 

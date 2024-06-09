%  This code demonstrates the use of the H2BO algorithm to generate 
%  superpixels from synthetic hyperspectral data, presented in:
%
%  (* UNDER REVIEW *)
%  Hierarchical Homogeneity-Based Superpixel Segmentation: Application to 
%  Hyperspectral Image Analysis
%  L. C. Ayres, S.J.M. de Almeida, J.C.M. Bermudez, R.A. Borsoi.
%  International Journal of Remote Sensing, 2024.
%
%  Author: Luciano Ayres
%  Latest Revision: Jun-2024
%  Revision: 1.0

%% DEMO - H2BO - Synthetic data
clc, clearvars, close all

% define random states
rand('state',10);
randn('state',10);

%% INPUT Parameters

SNR = 20;
path_data = 'data/';
path_output = 'output/';
addpath('utils')
image_name = 'DC3';  % dataset

slic_reg     = 0.00225;
slic_size    = [8 7 4 3];
tau_outliers = 10;
tau_homog    = 20;
lambda1_sp   = 0.01;
lambda2_sp   = 0.1;
beta         = 1;

%% Load fractional abundances

load(strcat(path_data,image_name,'.mat'))

%  Size of the images
nl = size(Xim,1);
nc = size(Xim,2);
N = nl*nc;         % number of pixels
p = size(Xim,3);   % number of endmembers

%% Build the dictionary

load(strcat(path_data,'USGS_1995_Library.mat'))
wavelength = datalib(:,1); %  order bands by increasing wavelength
[dummy, index] = sort(datalib(:,1));
A =  datalib(index,4:end);
names = names(4:end,:);

% prune the library
% min angle (in degres) between any two signatures
% the larger min_angle the easier is the sparse regression problem
min_angle = 4.44;
[A, index] = prune_library2(A,min_angle); % 240  signature
names = names(index',:);

% order  the columns of A by decreasing angles
[A, index, angles] = sort_library_by_angle(A);
names = names(index',:);
namesStr = char(names);

% select p endmembers  from A
supp = 2:p+1;
M = A(:, supp);
[L, p] = size(M);  % L = number of bands; p = number of material

%% Generate the observed data Y

% set noise standard deviation
sigma = sqrt(sum(sum((M*X).^2))/N/L/10^(SNR/10));
% generate Gaussian iid noise
noise = sigma*randn(L,N);
% save(strcat(path,image_name,'_noise.mat'),'noise');

% make noise correlated by low pass filtering (Gaussian)
bandwidth = 10000; % noise bandwidth in pixels of the noise
filter_coef = exp(-(0:L-1).^2/2/bandwidth.^2)';
scale = sqrt(L/sum(filter_coef.^2));
filter_coef = scale*filter_coef;
noise = idct(dct(noise).*repmat(filter_coef,1,N));

%  observed spectral vector
Y = M*X + noise;

% reorder and rescale data into 2-D array
Y2 = reshape(Y', nl, nc, L); % hyperspectral data cube
[numRows,numCols,numSpectra] = size(Y2);
scfact = mean(reshape(sqrt(sum(Y2.^2,3)), numRows*numCols, 1));
Y2 = Y2./scfact;

tic

%% Hierarchical Homogeneity-Based Oversegmentation (H2BO)
fprintf('--------------------------------------------------\n');
fprintf('-- Hierarchical Homogeneity-Based Oversegmentation\n');
fprintf('-- H2BO\n\n');
fprintf('Computing superpixels ...\n');

tic
sppx = H2BO(Y2, slic_size, slic_reg, tau_outliers, tau_homog,'no');
time = toc;

%% Homogeneity test - final oversegmentation
fprintf('\nFinal oversegmentation:\n');
sppx_labels = unique(sppx);
[labels_homog, labels_heter, sppx_dist_ratio] = homog_median_dist(Y2, sppx, sppx_labels, tau_homog, tau_outliers,'verbose','F');
img_homog_percent = 100*length(labels_homog)/length(sppx_labels);
fprintf('homog_sppx(%%) = %.1f %% \n', img_homog_percent);
fprintf('exec_time\t  = %.2f s\n',time);
fprintf('--------------------------------------------------\n');
%% Plot final segmentation
bands = [37 16 10];
show_segments(Y2, sppx, bands);

%% Export files
save(strcat(path_output,'sppx.mat'),'sppx');
exportgraphics(gcf,strcat(path_output,'sppx','.pdf'))   
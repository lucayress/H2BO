function [] = SLIC_homog(~, slic_reg, tau_outliers, tau_homog, slic_size0, slic_size1, slic_size2, slic_size3)
tic
slic_reg = str2double(slic_reg);
tau_outliers = str2double(tau_outliers);
tau_homog = str2double(tau_homog);
slic_size0 = str2num(slic_size0);
slic_size1 = str2num(slic_size1);
slic_size2 = str2num(slic_size2);
slic_size3 = str2num(slic_size3);

%% Paths
file_path = 'py_data/';
vlfeat_path = '';

% define random states
rand('state',10);
randn('state',10);

%% Load input data
load(strcat(file_path,'hsi_from_py.mat'),'img_hsi')

%% Compute superpixels - SLIC
% Set VL_feat toolbox
run(strcat(vlfeat_path,'vlfeat-0.9.21/toolbox/vl_setup'));

spSegs = vl_slic(single(img_hsi), slic_size0, slic_reg);
%show_segments(img_hsi, spSegs, [37 16 10]);

%% Homogeneity test - Median distance
labels_heter2 = [];
labels_heter3 = [];

% Homogeneity test - Initial
labels = unique(spSegs);
[labels_homog1, labels_heter1, sppx_median1, sppx_dist1, sppx_dist_avg1, sppx_dist_avg_trim1, sppx_dist_max1, sppx_dist_max_trim1, sppx_dist_ratio1] = homog_median_dist(img_hsi, spSegs, labels, tau_homog, tau_outliers,'F','F');
if ~isempty(labels_heter1)
    % Heterogeneous superpixels SLIC
    %%% Round 1
    [spSegs, labels_new1, numSuperpixels1] = heter_segments(img_hsi, spSegs, labels_heter1, slic_size1, slic_reg);
    spSegs1 = spSegs; %show_segments(img_hsi, spSegs1, colorBands);
    % Homogeneity test
    labels2 = labels_new1( (labels_new1 > max(labels)) );
    [labels_homog2, labels_heter2, sppx_median2, sppx_dist2, sppx_dist_avg2, sppx_dist_avg_trim2, sppx_dist_max2, sppx_dist_max_trim2, sppx_dist_ratio2] = homog_median_dist(img_hsi, spSegs, labels2, tau_homog, tau_outliers,'F','F');
end

if ~isempty(labels_heter2)
    % Heterogeneous superpixels SLIC
    %%% Round 2
    [spSegs, labels_new2, numSuperpixels2] = heter_segments(img_hsi, spSegs, labels_heter2, slic_size2, slic_reg);
    spSegs2 = spSegs; %show_segments(img_hsi, spSegs2, colorBands);
    % Homogeneity test
    labels3 = labels_new2( (labels_new2 > max(labels2)) );
    [labels_homog3, labels_heter3, sppx_median3, sppx_dist3, sppx_dist_avg3, sppx_dist_avg_trim3, sppx_dist_max3, sppx_dist_max_trim3, sppx_dist_ratio3] = homog_median_dist(img_hsi, spSegs, labels3, tau_homog, tau_outliers,'F','F');  
end

if ~isempty(labels_heter3)
    % Heterogeneous superpixels SLIC
    %%% Round 3
    [spSegs, labels_new3, numSuperpixels3] = heter_segments(img_hsi, spSegs, labels_heter3, slic_size3, slic_reg);
    spSegs3 = spSegs; %show_segments(img_hsi, spSegs3, colorBands);
    % Homogeneity test
    labels4 = labels_new3( (labels_new3 > max(labels3)) );
    [labels_homog4, labels_heter4, sppx_median4, sppx_dist4, sppx_dist_avg4, sppx_dist_avg_trim4, sppx_dist_max4, sppx_dist_max_trim4, sppx_dist_ratio4] = homog_median_dist(img_hsi, spSegs, labels4, tau_homog, tau_outliers,'F','F');
end

timeMscale = toc;
disp(timeMscale)

save(strcat(file_path,'labels_to_py.mat'),'spSegs');
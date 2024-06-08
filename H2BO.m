function sppx = H2BO(data, slic_size, slic_reg, tau_outliers, tau_homog)

slic_size0 = slic_size(1);
slic_size1 = slic_size(2);
slic_size2 = slic_size(3);
slic_size3 = slic_size(4);

%% Compute superpixels - SLIC
% Set VL_feat toolbox
vlfeat_path = '';
run(strcat(vlfeat_path,'vlfeat-0.9.21/toolbox/vl_setup'));

spSegs = vl_slic(single(data), slic_size0, slic_reg);
%show_segments(data, spSegs, [37 16 10]);

%% Homogeneity test - Median distance
labels_heter2 = [];
labels_heter3 = [];

% Homogeneity test - Initial
labels = unique(spSegs);
[labels_homog1, labels_heter1, sppx_dist_ratio1] = homog_median_dist(data, spSegs, labels, tau_homog, tau_outliers,'F','F');
if ~isempty(labels_heter1)
    % Heterogeneous superpixels SLIC
    %%% Round 1
    [spSegs, labels_new1, numSuperpixels1] = heter_segments(data, spSegs, labels_heter1, slic_size1, slic_reg);
    spSegs1 = spSegs; %show_segments(data, spSegs1, colorBands);
    % Homogeneity test
    labels2 = labels_new1( (labels_new1 > max(labels)) );
    [labels_homog2, labels_heter2, sppx_dist_ratio2] = homog_median_dist(data, spSegs, labels2, tau_homog, tau_outliers,'F','F');
end

if ~isempty(labels_heter2)
    % Heterogeneous superpixels SLIC
    %%% Round 2
    [spSegs, labels_new2, numSuperpixels2] = heter_segments(data, spSegs, labels_heter2, slic_size2, slic_reg);
    spSegs2 = spSegs; %show_segments(data, spSegs2, colorBands);
    % Homogeneity test
    labels3 = labels_new2( (labels_new2 > max(labels2)) );
    [labels_homog3, labels_heter3, sppx_dist_ratio3] = homog_median_dist(data, spSegs, labels3, tau_homog, tau_outliers,'F','F');  
end

if ~isempty(labels_heter3)
    % Heterogeneous superpixels SLIC
    %%% Round 3
    [spSegs, labels_new3, numSuperpixels3] = heter_segments(data, spSegs, labels_heter3, slic_size3, slic_reg);
    spSegs3 = spSegs; %show_segments(data, spSegs3, colorBands);
    % Homogeneity test
    labels4 = labels_new3( (labels_new3 > max(labels3)) );
    [labels_homog4, labels_heter4, sppx_dist_ratio4] = homog_median_dist(data, spSegs, labels4, tau_homog, tau_outliers,'F','F');
end

sppx = spSegs3;

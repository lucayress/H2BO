function sppx = H2BO(data, slic_size, slic_reg, tau_outliers, tau_homog, verbose)

%% Set VL_feat toolbox
vlfeat_path = '';
run(strcat(vlfeat_path,'vlfeat-0.9.21/toolbox/vl_setup'));

%% Hierarchical Homogeneity-Based Superpixel Segmentation
R = length(slic_size)-1;

% Initial SLIC segmentation - r=0
fprintf('r = 0 \n');
spSegs = vl_slic(single(data), slic_size(1), slic_reg);
labels = unique(spSegs);
[~, labels_heter, ~] = homog_median_dist(data, spSegs, labels, tau_homog, tau_outliers,verbose,'F');

% Extra rounds of SLIC segmentation - from r=1 to R
for r = 1:R
    fprintf('r = %d \n', r);
    if ~isempty(labels_heter)
        % SLIC over heterogeneous superpixels
        [spSegs, labels_new, ~] = heter_segments(data, spSegs, labels_heter, slic_size(r+1), slic_reg);
        % Homogeneity test
        labels = labels_new( (labels_new > max(labels)) );
        [~, labels_heter, ~] = homog_median_dist(data, spSegs, labels, tau_homog, tau_outliers,verbose,'F');
    else
        fprintf('There are no heterogeneous superpixels in scale r = %d.\n',r);
        break;
    end
end
sppx = spSegs;

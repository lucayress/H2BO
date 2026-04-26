function [labels_homog, labels_heter, sppx_dist_ratio] = homog_median_dist(im, segments, labels, tau_homog, tau_outliers, verbose, show)
nl = size(im,1);
nc = size(im,2);
N = nl*nc;
L = size(im,3);

numSuperpixels = length(labels);

% Pre-allocate only the scalar outputs (1 value per superpixel)
sppx_dist_avg_trim = zeros(1, numSuperpixels);
sppx_dist_max = zeros(1, numSuperpixels);
sppx_dist_max_trim = zeros(1, numSuperpixels);
sppx_dist_ratio = zeros(1, numSuperpixels);

% Reshape image to 2D for vectorised pixel extraction
im_2d = reshape(im, N, L);  % (N x L)

for i=1:numSuperpixels
    [rowi, coli] = find(segments==labels(i));
    n_pix = length(rowi);

    idx = sub2ind([nl, nc], rowi, coli);
    sp_pixels = im_2d(idx, :)';  % (L x n_pix) - same layout as original sppx(:,1:j,i)

    sp_median = median(sp_pixels, 2);  % (L x 1)

    % Compute distances from median (vectorised)
    diffs = sp_pixels - repmat(sp_median, 1, n_pix);  % (L x n_pix)
    sp_dist = sqrt(sum(diffs.^2, 1));  % (1 x n_pix) Euclidean norms

    sppx_dist_avg_trim(i) = mean(remove_top(sp_dist, tau_outliers));
    sppx_dist_max(i) = max(sp_dist);
    sppx_dist_max_trim(i) = max(remove_top(sp_dist, tau_outliers));

    sppx_dist_ratio(i) = 100*(sppx_dist_max_trim(i) - sppx_dist_avg_trim(i))/sppx_dist_avg_trim(i);
    if isnan(sppx_dist_ratio(i))
        sppx_dist_ratio(i) = 0; % if value is NaN then turn into 0.
    end
end

sppx_dist_ratio = sppx_dist_ratio';

ind_homog = find(sppx_dist_ratio <= tau_homog);
labels_homog = labels(ind_homog,:);
ind_heter = find(sppx_dist_ratio > tau_homog);
labels_heter = labels(ind_heter,:);
if strcmp(verbose,'verbose')
    fprintf('num_sppx\t  = %d\n',length(ind_heter)+length(ind_homog));
    fprintf('heter_sppx\t  = %g \n', length(ind_heter));
    fprintf('homog_sppx\t  = %g \n', length(ind_homog));
end

%% Display superpixels homogeneity classification

if strcmp(show,'show')
    % Homogeneous = 1 (white)
    im_homog = im;
    for i=1:length(labels_homog)
        [rowi, coli] = find(segments==labels_homog(i));
        for j=1:length(rowi)
            im_homog(rowi(j),coli(j),:) = 1;
        end
    end
    % Heterogeneous = 0.5 (gray)
    for i=1:length(labels_heter)
        [rowi1, coli1] = find(segments==labels_heter(i));
        for j=1:length(rowi1)
            im_homog(rowi1(j),coli1(j),:) = 0.5;
        end
    end
    map = im_homog(:,:,[1 2 3]);
    
    figure;
    imagesc(map); axis image off;
    clear map
end

end
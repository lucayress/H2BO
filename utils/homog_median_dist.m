function [labels_homog, labels_heter, sppx_dist_ratio] = homog_median_dist(im, segments, labels, tau_homog, tau_outliers, verbose, show)
nl = size(im,1);
nc = size(im,2);
N = nl*nc;
L = size(im,3);

aa = 200;

numSuperpixels = length(labels);
sppx = zeros(L, ceil(N/aa), numSuperpixels);
sppx_median = zeros(L, 1, numSuperpixels);
sppx_dist = zeros(1, ceil(N/aa), numSuperpixels);

sppx_dist_avg_trim = zeros(1,1,numSuperpixels);
sppx_dist_max = zeros(1,1,numSuperpixels);
sppx_dist_max_trim = zeros(1,1,numSuperpixels);

for i=1:numSuperpixels
    [rowi, coli] = find(segments==labels(i));
    for j=1:length(rowi)
        sppx(:,j,i) = im(rowi(j),coli(j),:);
    end
    sppx_median(:,1,i) = median(sppx(:,1:j,i),2);

    % angles and distances
    for j=1:length(rowi)
        u = sppx_median(:,1,i);
        v = squeeze(im(rowi(j),coli(j),:));
        sppx_dist(:,j,i) = norm(u-v);
    end

    sppx_dist_avg_trim(:,1,i) = mean(remove_top(sppx_dist(:,1:j,i), tau_outliers));
    sppx_dist_max(:,1,i) = max(sppx_dist(:,1:j,i));
    sppx_dist_max_trim(:,1,i) = max(remove_top(sppx_dist(:,1:j,i), tau_outliers));

    sppx_dist_ratio(:,1,i) = 100*(sppx_dist_max_trim(:,1,i) - sppx_dist_avg_trim(:,1,i))/sppx_dist_avg_trim(:,1,i);
    indef = isnan(sppx_dist_ratio);
    sppx_dist_ratio(indef == 1) = 0; % if values is NaN then turn into 0.
end

sppx_dist_ratio = squeeze(sppx_dist_ratio)';

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
%% Superpixels homogeneity classification
function map = homog_map(im, segments, labels_homog, labels_heter)

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
% mark boundaries
%[sx,sy]=vl_grad(double(segments), 'type', 'forward');
%s = find(sx | sy);
map = im_homog(:,:,[1 2 3]);

% black edge
% map(1:end,1,:) = 0;
% map(1:end,end,:) = 0;
% map(1,1:end,:) = 0;
% map(end,1:end,:) = 0;

%map([s s+numel(im(:,:,1)) s+2*numel(im(:,:,1))]) = 0;
end
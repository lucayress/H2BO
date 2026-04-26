function [new_segments, labels, numSuperpixels] = heter_segments(im, segments, labels_heter, slic_size, slic_reg)

nl = size(im,1);
nc = size(im,2);
%N = nl*nc;         % number of pixels
L = size(im,3);    % number of bands
% Issue 2 fix: removed unused SP_heter allocation (was: zeros(nl,nc,nHeter))
label_max = max(segments(:));
for i=1:length(labels_heter)
    [rowi1, coli1] = find(segments==(labels_heter(i)));
    SP_segs = segments(min(rowi1):max(rowi1), min(coli1):max(coli1));
    % Issue 2 fix: removed write to unused SP_heter
    mask = SP_segs;
    mask( SP_segs ~= labels_heter(i)) = 0;
    mask( SP_segs == labels_heter(i)) = 1;
    SP_Y = im(min(rowi1):max(rowi1), min(coli1):max(coli1),:);
    SP_Y = SP_Y.*double(repmat(mask, [1 1 L]));
    % Issue 6 fix: adaptive fill value to avoid collision with real data
    fill_val = max(SP_Y(:)) + 1;
    SP_Y( SP_Y == 0 ) = fill_val;
    SP_segs_new = vl_slic(single(SP_Y), slic_size, slic_reg);
    SP_segs_new = (SP_segs_new+1).*mask;
    %SP_segs_new( SP_segs_new == 1) = 0;
    % Issue 3 fix: renamed inner loop variable from i to ii
    for ii=1:size(SP_segs_new,1)
        for j=1:size(SP_segs_new,2)
            if (SP_segs_new(ii,j) ~= 0)
                segments(min(rowi1)-1+ii, min(coli1)-1+j) = SP_segs_new(ii,j) + label_max;
            end
        end
    end
    label_max = max(segments(:));
end
new_segments = segments;
labels = unique(new_segments(:));
numSuperpixels = length(labels);
end
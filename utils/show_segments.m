function [ imp ] = show_segments(im, segments, colorBands)
imgColor = im(:,:,colorBands);
imgColor = uint8(255*(imgColor - min(imgColor(:)))./(max(imgColor(:))-min(imgColor(:))));
[sx,sy]=vl_grad(double(segments), 'type', 'forward'); % mark boundaries
s = find(sx | sy);
imp = imgColor;
imp([s s+numel(im(:,:,1)) s+2*numel(im(:,:,1))]) = 0;
% figure;
figure, set(gcf,'color', 'white')
imagesc(imp) ; axis image off ;
end
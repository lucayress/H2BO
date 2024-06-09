function [A] = remove_top(A, threshold)
remove_n = floor(length(A)*threshold/100);
A = sort(A);
A = A(1:end-remove_n);
end




clear
close all

bvhPath = './bvh_files/';
bvhFiles = dir([bvhPath '/*.bvh']);

% set path for new bvh files which have fixed root joints
newbvhPath = './origin/';

for k = 1 : length(bvhFiles)
    savebvh_rootfixed(newbvhPath, [bvhPath bvhFiles(k).name]);
    fprintf('%d/%d is done\n', k, length(bvhFiles));
end




function savebvh_rootfixed(newbvhPath, fname)
%% LOADBVH  Load a .bvh (Biovision) file.
%
% Loads BVH file specified by FNAME (with or without .bvh extension)
% and parses the file, calculating joint kinematics and storing the
% output in SKELETON.

%% Load and parse header data
%
% The file is opened for reading, primarily to extract the header data (see
% next section). However, I don't know how to ask Matlab to read only up
% until the line "MOTION", so we're being a bit inefficient here and
% loading the entire file into memory. Oh well.

% add a file extension if necessary:
if ~strncmpi(fliplr(fname),'hvb.',4)
  fname = [fname,'.bvh'];
end

fid = fopen(fname);
C = textscan(fid,'%s');
fclose(fid);
C = C{1};


%% Parse data
%
% This is a cheap tokeniser, not particularly clever.
% Iterate word-by-word, counting braces and extracting data.

% Initialise:
skeleton = [];
ii = 1;
nn = 0;
brace_count = 1;

while ~strcmp( C{ii} , 'MOTION' )
  
  ii = ii+1;
  token = C{ii};
  
  if strcmp( token , '{' )
    
    brace_count = brace_count + 1;
    
  elseif strcmp( token , '}' )
    
    brace_count = brace_count - 1;
    
  elseif strcmp( token , 'OFFSET' )
    
    skeleton(nn).offset = [str2double(C(ii+1)) ; str2double(C(ii+2)) ; str2double(C(ii+3))];
    ii = ii+3;
    
  elseif strcmp( token , 'CHANNELS' )
    
    skeleton(nn).Nchannels = str2double(C(ii+1));
    
    % The 'order' field is an index corresponding to the order of 'X' 'Y' 'Z'.
    % Subtract 87 because char numbers "X" == 88, "Y" == 89, "Z" == 90.
    if skeleton(nn).Nchannels == 3
      skeleton(nn).order = [C{ii+2}(1),C{ii+3}(1),C{ii+4}(1)]-87;
    elseif skeleton(nn).Nchannels == 6
      skeleton(nn).order = [C{ii+5}(1),C{ii+6}(1),C{ii+7}(1)]-87;
    else
      error('Not sure how to handle not (3 or 6) number of channels.')
    end
    
    ii = ii + skeleton(nn).Nchannels + 1;

  elseif strcmp( token , 'JOINT' ) || strcmp( token , 'ROOT' )
    % Regular joint
    
    nn = nn+1;
    
    skeleton(nn).name = C{ii+1};
    skeleton(nn).nestdepth = brace_count;

    if brace_count == 1
      % root node
     skeleton(nn).parent = 0;
    elseif skeleton(nn-1).nestdepth + 1 == brace_count;
      % if I am a child, the previous node is my parent:
      skeleton(nn).parent = nn-1;
    else
      % if not, what is the node corresponding to this brace count?
      % skeleton(nn).parent = skeleton(brace_count).parent;
      prev_parent = skeleton(nn-1).parent;
      while(skeleton(prev_parent).nestdepth+1~=brace_count)
          prev_parent = skeleton(prev_parent).parent;
      end
      skeleton(nn).parent = prev_parent;
    end
    
    ii = ii+1;
            
  elseif strcmp( [C{ii},' ',C{ii+1}] , 'End Site' )
    % End effector; unnamed terminating joint
    %
    % N.B. The "two word" token here is why we don't use a switch statement
    % for this code.
    
    nn = nn+1;
    
    skeleton(nn).name = ' ';
    skeleton(nn).offset = [str2double(C(ii+4)) ; str2double(C(ii+5)) ; str2double(C(ii+6))];
    skeleton(nn).parent = nn-1; % always the direct child
    skeleton(nn).nestdepth = brace_count;
    skeleton(nn).Nchannels = 0;
        
  end
  
end

%% Initial processing and error checking

Nnodes = numel(skeleton);
Nchannels = sum([skeleton.Nchannels]);
Nchainends = sum([skeleton.Nchannels]==0);

% Calculate number of header lines:
%  - 5 lines per joint
%  - 4 lines per chain end
%  - 4 additional lines (first one and last three)
Nheaderlines = (Nnodes-Nchainends)*5 + Nchainends*4 + 4;

rawdata = importdata(fname,' ',Nheaderlines);

index = strncmp(rawdata.textdata,'Frames:',7);
Nframes = sscanf(rawdata.textdata{index},'Frames: %f');

index = strncmp(rawdata.textdata,'Frame Time:',10);
frame_time = sscanf(rawdata.textdata{index},'Frame Time: %f');

time = frame_time*(0:Nframes-1);

if size(rawdata.data,2) ~= Nchannels
  error('Error reading BVH file: channels count does not match.')
end

if size(rawdata.data,1) ~= Nframes
  warning('LOADBVH:frames_wrong','Error reading BVH file: frames count does not match; continuing anyway.')
end

%% Fix the root of skeleton to the origin of coordinate
%
% modified by JIANL: to generate new bvh, in which the root joint is fixed
% at origin of x-y coordinate, keep z value unchanged

rawdata.data(:,1:6) = 0;
[pathstr,name,ext] = fileparts(fname);
%fid = fopen(['D:\Jian\CV\Datasets\CMU\BVH\origin\' name ext],'wt');
fNum = uint16(Nframes/5);
myName = [name '-' int2str(fNum)];

fid = fopen([newbvhPath myName ext],'wt');

for i = 1 : length(rawdata.textdata)
    str = rawdata.textdata{i};
    fprintf(fid, '%s\n', str);
end
for i = 1 : length(rawdata.data)
    data = rawdata.data(i,:);
    fprintf(fid, '%.4f ', data);
    fprintf(fid, '\n');
end
fclose(fid);

fileN = '01_01'; %'14_06';

%load(['D:\HumanActionMocap\Hossein\mesh\' fileN '.mat'])

%load('D:\HumanActionMocap\HumanModelPolygons.mat')

[sk,tm] = loadbvh(['./bvh_files/' fileN '.bvh']);

%%

skpoly = [1 2 1; 2 3 2; 3 4 3; 4 5 4; 5 6 5; 6 7 6; 8 1 8; 9 8 9; 9 10 9; ...

    11 10 11; 12 11 12; 13 12 13; 14 1 14; 15 14 15; 16 15 16; 17 16 17; ...

    18 17 18; 19 18 19; 20 19 20; 21 16 21; 22 21 22; 23 22 23; 24 23 23; 24 25 24;...

    25 24 25; 26 25 26; 27 26 27; 28 24 28; 29 28 29; 30 16 30; 31 30 31; 31 32 31;...

    32 31 32; 33 32 33; 34 33 34; 35 34 35; 35 36 35; 37 33 37; 38 37 38];

%%
% this is for NTU skeleton data
% skpoly = [1 2 1; 1 13 1; 13 14 13; 14 15 14; 15 16 15; 1 17 1; 17 18 17; ...
%     18 19 18; 19 20 19; 2 21 2; 21 5 21; 5 6 5; 6 7 6; 7 8 7; 8 23 8; ...
%     8 22 8; 21 9 21; 9 10 9; 10 11 10; 11 12 11; 12 25 12; 12 24 12; 21 3 21; 3 4 3];

%%

FigHandle = figure('Position', [100,100, 1280, 720],'Color',[0,0,0]);

FigHandle.InvertHardcopy = 'off'; FigHandle.PaperPositionMode = 'auto';

set(gca,'Position',[0 0 1 1]);

%axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

%pmin = [100 100 100]; pmax = [-100 -100 -100];

for t = 5 : 5 : length(tm)

    pts = zeros(38,3);

    for ii = 1 : length(sk)

        pts(ii,:) = sk(ii).Dxyz(:,t)';

    end

    %pts = pts*0.62; pts(:,1) = pts(:,1)-10;

    plot3(pts(:,1), pts(:,2),pts(:,3),'or'); axis on; grid on; axis equal; hold on;

 %   axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

    

    trimesh(skpoly,pts(:,1), pts(:,2),pts(:,3)); % l = light('Position',[-231, -5013, 145138*1.2]);

  %  axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

   %set(gca,'CameraPosition',[-10,10,1000]);%[-231, -5013, 145138*1.2]);

   campos([-1,10,100]) ;

   set(gca,'CameraUpVector', [0 1 0]);

   lighting gouraud; shading interp; %colormap gray;

    x = mesh(t/5+1).pointList.points(:,1);

    y = mesh(t/5+1).pointList.points(:,2);

    z = mesh(t/5+1).pointList.points(:,3);

    if t > 800

        plot3(x,y,z,'.g');axis equal; %axis off;

   %     axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

    end

%     if t > 1200

%         x = x -10;

%         trimesh(HumanModelPolygons, x, y, z); %axis off;  l = light('Position',[-231, -5013, 145138*1.2]);

%         axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

%     end

    if t > 1600

        x = x+10;

        trisurf(HumanModelPolygons, x,y,z); shading interp;%axis off;  l = light('Position',[-231, -5013, 145138*1.2]);

    %    axis([pmin(1), pmax(1), pmin(2), pmax(2), pmin(3), pmax(3)]);

    end

    %pmin = min([pmin; pts; [x y z]]);     pmax = max([pmax; pts; [x y z]]);

    hold off;

   

  %  saveas(FigHandle, sprintf('%s%d.jpg','C:\EVERYTHING\presentations\WAITA\frames\', t/5));

    pause(0.01);

end
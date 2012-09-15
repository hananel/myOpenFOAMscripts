%if ~exist('filename')
%    indextypes = {'png','jpg','gif'};
%    [filename, pathname, filterindex] = uigetfile( ...
%        {'*.png';'*.jpg';'*.gif'},'Pick a file');
%end
filename = 'Martinez_Figure_21a.png';
pathname = '/home/hanan/MartinezBump2D';
c=imread([pathname '/' filename]);
fig=image(c);
colormap('bone');

%the next values should be input for the specific chart
% use the new opened sketch to decide what they should be
minX=input('minX: ');
maxX=input('maxX: ');
minY=input('minY: ');
maxY=input('maxY: ');

[x,y]=ginput;

%first point: min x
%second point: max x
%third point: min y
%fourth point: max y
% next points - the graph itself.


TetaX=atan2((y(2)-y(1)),(x(2)-x(1)));
CosX=cos(TetaX);
SinX=sin(TetaX);
SinTeta=SinX;
CosTeta=CosX;
%teta=0.5*(tetaX+tetaY);
%teta=tetaX;


for (i=1:length(x))
    xOut(i)=x(i)*CosTeta-y(i)*SinTeta;
    yOut(i)=x(i)*SinTeta+y(i)*CosTeta;
end
for (i=5:length(x))
    xOut(i)=(xOut(i)-xOut(1))/(xOut(2)-xOut(1))*(maxX-minX)+minX;
    yOut(i)=(yOut(i)-yOut(3))/(yOut(4)-yOut(3))*(maxY-minY)+minY;
end

format long
save xyTemp xOut yOut
[xOut' yOut']

import salome,geompy,random,math,sys
from numpy import *
import scipy.special as sp
#from numeric import *

AR = 1
N = 500
A = 3.1926
H = 200  # [m]
a = H*AR # [m]
x = linspace(-a,a,N)	# [m]	
y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*x/a) - sp.i0(A)*sp.j0(A*x/a) )
nPts = len(x)
x = append(x,max(a*40,3600))
x = append(-max(a*40,3600),x)
y = append(y,0)
y = append(0,y)
nPts = nPts + 2

ptList = []
print "Creating %s points"%nPts
for i in range(nPts):
    v = geompy.MakeVertex(x[i], y[i], 0)
    geompy.addToStudy(v, "Vertex_%d"%(i+1) )
    ptList.append(v)
print str([i,x[i],y[i],0])

print "creating polyLine"
polyline = geompy.MakePolyline(ptList)
geompy.addToStudy(polyline, "polyline" )

print "creating extrusion"
Extrusion_1 = geompy.MakePrismDXDYDZ2Ways(polyline, 0, 0, 100)
geompy.addToStudy(Extrusion_1, "Extrusion_1" )
newName = "Martinez2D_h_" + str(H) + "_AR_" + str(AR)
print "exporting stl"
geompy.Export(Extrusion_1, "/home/hanan/"+newName+".stl", "STL_ASCII")
print "saved file name " + newName



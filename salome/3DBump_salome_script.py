import salome,geompy,random,math,sys
from numpy import *
import scipy.special as sp
#from numeric import *

AR = 8
N = 500
A = 3.1926
H = 200  # [m]
a = H*AR # [m]
x = linspace(0,a,N)	# [m]	
y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*x/a) - sp.i0(A)*sp.j0(A*x/a) )
nPts = len(x)
x = append(x,max(a*200,3600))
y = append(y,0)
nPts = nPts + 1

ptList = []
print "Creating %s points"%nPts
for i in range(nPts):
    v = geompy.MakeVertex(x[i], 0, y[i])
    geompy.addToStudy(v, "Vertex_%d"%(i+1) )
    ptList.append(v)
print str([i,x[i],y[i],0])

print "creating polyLine"
polyline = geompy.MakePolyline(ptList)
#interpol = geompy.MakeInterpol(ptList)
geompy.addToStudy(polyline, "polyline" )
#geompy.addToStudy(interpol, "interpol" )

print "creating revolution"
Vertex_a = geompy.MakeVertex(0, 0, 0)
Vertex_b = geompy.MakeVertex(0, 0, H)
Line_1 = geompy.MakeLineTwoPnt(Vertex_a, Vertex_b)
Revolution_1 = geompy.MakeRevolution(polyline, Line_1, 360*math.pi/180.0)
newName = "Martinez3D_h_" + str(H) + "_AR_" + str(AR)
print "exporting stl"
geompy.Export(Revolution_1, newName+".stl", "STL_ASCII")
print "saved file name " + newName

geompy.addToStudy( Revolution_1, 'Revolution_1' )


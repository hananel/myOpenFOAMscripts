#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# loadMeasurements(flag, directory, fileName) 
# 	read measurements at two heights - U1(t), U2(t) at z1 and z2
#	flag - which style of data. 

import sys, math, os
from os import path
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import glob,subprocess
from matplotlib.backends.backend_pdf import PdfPages
import datetime as dt

flag = sys.argv[1]
directory = sys.argv[2]
fileName = sys.argv[3]

def mkdate(text):
    return dt.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')

def plotMe_dateVec(xData,yData,myTitle,figNum,col):
	if figNum<0:
		fig = figure()
	else:
		fig = figure(figNum)
	ax = fig.add_subplot(111)
	ax.plot_date(xData,yData,col,xdate=True)
	fig.autofmt_xdate()
	title(myTitle)
	return fig

def plotData(dateVec, U1, U2, z0):
	fig0 = plotMe_dateVec(array(dateVec),U1,"wind speed data",0,'b')
	fig0 = plotMe_dateVec(array(dateVec),U2,"wind speed data",0,'g')
	fig0.show()
	fig1 = plotMe_dateVec(array(dateVec),z0,"wind shear",1,'r')
	fig1.show()

def main(flag,directory,fileName):

	if flag == "clean-electric":

		"""  
		Data files per day. Each containes:
		0		    1		2		3		4	5	6	7		8		9
		YYYY-MM-DD hh:mm:ss,speed 0,	gust 0,		pulse 0,	speed 1,gust 1,	pulse 1,speed 2,	gust 2,	        pulse 2
		2011-01-06 01:51:13,0.0	,	0.0,		0,		0.0,	0.0,	0,	0.0,		0.0,		0,
		
		10		11		12		13		14		15		16		17	18	19
		counter,	counter,	counter,	wind direction, voltage	,	potentiometer 0 potentiometer 1 Temp.		
		0.00,		0.00,		0.00,		0, 		12.57,		0.00,		0.00,		226.3 ,	4.998,	4.998,

		20	21	22
		4.998,	4.998,	76	
		
		"""
		# measurements average time
		dailyAvgTime = 1.0/6 	# [hr]
		H1 = 15			# [m]
		H2 = 10			# [m]

		# read directory files
		directoryFileList = os.listdir(directory)
		directoryFileList.sort()	# works with american dates only :)
		dateVec = []
		U1 = array([])
		U1max = array([])
		U1std = array([])
		U2 = array([])
		U2max = array([])
		U2std = array([])
		z0 = array([])
		z0daily = array([])
		direction = array([])
		temp = array([])
		voltage = array([])	

		# loop files	
		for currentFile in directoryFileList:
			# read data
			print "reading ", directory+"/"+currentFile
			dateData = genfromtxt(directory + "/" + currentFile,delimiter=',',dtype=None) # for date string
			data = genfromtxt(directory + "/" + currentFile,delimiter=',')
			# convert date string to number
			for i in range(len(dateData)):
				dateVec.append(date2num(mkdate(dateData[i][0])))
			
			# wind speed, gust and estimate of std according to 1/3 the (gust-avg) difference
			U1 	= append(U1, 	data[:,1])
			U1max 	= append(U1max,	data[:,2])
			U1std 	= append(U1std, (data[:,2]-data[:,1])/3)
			U2 	= append(U2, 	data[:,4])
			U2max	= append(U2max,	data[:,5])
			U2std	= append(U2std, (data[:,5]-data[:,4])/3) 
			direction = append(direction, data[:,13])
			voltage	= append(voltage, data[:,14])
			temp	= append(temp, data[:,17])
	elif flag == "IMS":
		print "not implemented yet"
	elif flag == "BirZ":
		"""
		Time		   Interval(mi)	IndoorHumidity(%)	IndoorTemperature(C)	OutdoorHumidity(%)	OutdoorTemperature(C)	AbsolutePressure(hPa)	
		01/28/11,07:51:00	,5,		47,			14.4,			99,			12			,929	
		Wind(m/s)	Gust(m/s)	Direction	RelativePressure(hPa)	Dewpoint(C)	Windchill(C)	
		,0.3,		1,		SW,		1017.1,			11.9,		12,
		HourRainfall(mm)	24hourRainfall(mm)	WeekRainfall(mm)	MonthRainfall(mm)	TotalRainfall(mm)
		0,			0,			0.6,			42,			96.6,	
		WindLevel(bft)	GustLevel(bft)
		1,		1
		"""
		# measurements average time
		dailyAvgTime = -5 	# [hr] -5 stands for "iregular time stamp" - thus will use interpolation
		H1 = 10			# [m]
		H2 = -5			# [m] -5 stands for "no measurement at second height"

		# read directory files
		directoryFileList = os.listdir(directory)
		directoryFileList.sort()	# works with american dates only :)
		dateVec = []
		U1 = array([])
		U1max = array([])
		U1std = array([])
		U2 = array([])
		U2max = array([])
		U2std = array([])
		z0 = array([])
		z0daily = array([])
		direction = array([])
		temp = array([])
		voltage = array([])	

		# loop files	
		for currentFile in directoryFileList:
			# read data
			print "reading ", directory+"/"+currentFile
			dateData = genfromtxt(directory + "/" + currentFile,delimiter=',',dtype=None) # for date string
			data = genfromtxt(directory + "/" + currentFile,delimiter=',')
			# convert date string to number
			for i in range(len(dateData)):
				dateVec.append(date2num(mkdate(dateData[i][0])))
			
			# wind speed, gust and estimate of std according to 1/3 the (gust-avg) difference
			U1 	= append(U1, 	data[:,1])
			U1max 	= append(U1max,	data[:,2])
			U1std 	= append(U1std, (data[:,2]-data[:,1])/3)
			U2 	= append(U2, 	data[:,4])
			U2max	= append(U2max,	data[:,5])
			U2std	= append(U2std, (data[:,5]-data[:,4])/3) 
			direction = append(direction, data[:,13])
			voltage	= append(voltage, data[:,14])
			temp	= append(temp, data[:,17])

	else:
		print "wrong flag type"
	
	# calculate z0 (make daily - at the moment, it's for the whole time series)
	gam = array(U2)/array(U1)
	z0 = (H1**gam/H2) ** (1-(gam-1))
	z0 = nan_to_num(z0)
	print "z0 average and std is ", z0.mean(), "+/-", z0.std()

	# daily analysis
	averagingPeriods = int(24.0 / dailyAvgTime)

	n = z0.shape
	if len(n)>1:
		nLen = n[0]*n[1]
	else:
		nLen = n[0]

	z0_days = z0[0:averagingPeriods*int(nLen/averagingPeriods)] # cutting to full-day daya
	z0_days = z0_days.reshape(averagingPeriods,nLen/averagingPeriods)
	z0_diurnal = range(averagingPeriods)
	z0_diurnal_std = range(averagingPeriods)
	for i in range(averagingPeriods):
		z0_tmp = z0_days[:,i]
		z0_diurnal[i] = z0_tmp.mean()
		z0_diurnal_std[i] = z0_tmp.std()

	# plotting loaded data
	plotData(dateVec, U1, U2, z0)
	
	# plot diurnal analysis
	timeDiurnal = linspace(0,24,averagingPeriods)

	fig2 = figure()
	errorbar(timeDiurnal, z0_diurnal, yerr=z0_diurnal_std, fmt='ro')
	axis([0,24,0,z0.mean()*2])
	title(["z0 average and std is ", z0.mean(), "+/-", z0.std()])
	plt.show()

if __name__ == '__main__':
 main(flag,directory,fileName)


import pylab
from ScopeTools import oscilloscope
import time

if __name__ == "__main__":
	scope0 = oscilloscope(scopeid=0)
	if not scope0.isAttached():
		print "WARNING: Scope not found!"
		exit()
	scope0.setVoltageDivision(1, 5)
	print scope0.setSamplingRate(26)
	scope0.setupDsoCalLevel()
	pylab.ion()
	length = 1000
	for i in xrange(0, 10):	
		data = scope0.readDataFromScope(dataPoints = 3000)
		tIndex = data[3].value
		pylab.plot(data[2][:length], data[0][tIndex:tIndex+length])#, 'r-')
		pylab.draw()
		time.sleep(1)
from ctypes import *

#Set the directory for your HantekScope DLL here.
marchdll_file = "Hantek SDK DLLs\HTMarch.dll"

class oscilloscope():
	def __init__(self, scopeid=0): #Set up our scope. The scope id is for each scope attached to the system.
		self.marchdll = WinDLL(marchdll_file)
		self.scopeid = c_ushort(scopeid)
		self.Channels = {1:0,2:1}
		self.voltIndicies ={0:("20 mV/Div", 20e-3), 1:("50 mV/Div", 50e-3), 2:("100 mV/Div", 0.1), 3:("200 mV/Div", 0.2),
							4:("500 mV/Div", 0.5), 5:("1 V/Div", 1.0), 6:("2 V/Div", 2.0), 7:("5 V/Div", 5.0)}
		
		initVolt = 4
		self.currentVoltIndex = [None, None, None] #Use a list instead of dict for speed up on data reads.
									   #No channel 0, so let's just make that None.
		for entry in self.Channels:
			self.currentVoltIndex[entry] = c_int(initVolt) #Just set it to some initial value.
			
		self.currentVoltDiv = [None, None, None]
		for entry in self.Channels:
			self.currentVoltDiv[entry] = self.voltIndicies[initVolt][1]
		
		self.sampleRateIndicies ={11:("16 MSa/s", 16e6), 12:("8 MSa/s", 8e6), 13:("4 MSa/s", 4e6),
							25:("500 KSa/s", 500e3), 26:("200 KSa/s", 200e3), 27:("100 KSa/s", 100e3)}
		for index in range(0, 11):
			self.sampleRateIndicies[index] = ("48 MSa/s", 48e6) #All values 0-10 are set to this.
		for index in range(14, 25):
			self.sampleRateIndicies[index] = ("1 MSa/s", 1e6)
		
		initRate = 10
		self.currentSampleRateIndex = c_int(initRate)
		self.currentSampleRate = self.sampleRateIndicies[initRate][1]
		
		self.validTriggerSweeps = {0:"Auto", 1:"Normal", 2:"Single"}
		self.currentTriggerSweep = c_short(0)
		
		self.validTriggerSources = {0:"CH1", 1:"CH2"}
		self.currentTriggerSource = c_short(0)
		
		self.validTriggerSlopes = {0:"Rise", 1:"Fall"}
		self.currentTriggerSlope = c_short(0)
		
		self.validHTriggerPositions = range(0, 101)
		self.currentHTriggerPosition = c_short(10)
		
		self.validTriggerLevels = range(0, 256)
		self.currentTriggerLevel = c_short(10)
		
		self.validDValueModes = {0:"Step D-Value", 1:"Line D-Value", 2:"sin(x)/x D-Value"}
		self.currentDValueMode = c_short(0)
		
		self.calData = None
	
	def isAttached(self):
		"""Takes no arguments.
			Returns true if the scope is attached, false otherwise."""
		retval = self.marchdll.dsoOpenDevice(self.scopeid) 
		if not retval :
			return False
		elif retval == 1:
			return True
		else:
			print "ERROR: Unexpected return value through API."
			return False
	
	
	
	def getVoltageDivDict(self):
		"""Takes no arguments, returns the dictionary that relates voltage index to its
			corresponding voltage division."""
		return self.voltIndicies
		
	def getChannelsDict(self):
		"""Takes no arguments, returns the dictionary that contains all valid channels."""
		return self.Channels
	
	def getSampleRateDict(self):
		"""Takes no arguments, returns the dictionary that relates sample index to its
			corresponding timing division."""
		return self.sampleRateIndicies
	
	def getTriggerSweepsDict(self):
		"""Takes no arguments, returns the dictionary that relates the trigger sweep index to its
			corresponding setting."""
		return self.validTriggerSweeps
		
	def getTriggerSourcesDict(self):
		"""Takes no arguments, returns the dictionary that relates the trigger source index to its
			corresponding setting."""
		return self.validTriggerSources
		
	def getTriggerSlopesDict(self):
		"""Takes no arguments, returns the dictionary that relates the trigger slope index to its
			corresponding setting."""
		return self.validTriggerSlopes
	
	def setVoltageDivision(self, channelNum, voltIndex):
		"""Takes two arguments, first the channel number, second the voltage index value.
			Returns true if arguments were valid and command returned successfully, false otherwise."""
		if  channelNum not in self.Channels or voltIndex not in self.voltIndicies:
			return False
		else:
			self.currentVoltIndex[channelNum] = c_int(voltIndex)
			self.currentVoltDiv[channelNum] = self.voltIndicies[voltIndex][1]
			retval = self.marchdll.dsoSetVoltDIV(self.scopeid, 
													c_int(self.Channels[channelNum]),
													self.currentVoltIndex[channelNum])
			if retval == 1:
				return True #The DLL documentation may contain a typo on the return val.
			else:
				return False
	
	
	def setSamplingRate(self, sampleRateIndex):
		"""Takes one arguments,the sampling rate index value.
			Returns true if arguments were valid and command returned successfully, false otherwise."""
		if  sampleRateIndex not in self.sampleRateIndicies:
			return False
		else:
			self.currentSampleRateIndex = c_int(sampleRateIndex)
			self.currentSampleRate = self.sampleRateIndicies[sampleRateIndex][1]
			retval = self.marchdll.dsoSetTimeDIV(self.scopeid, 
													self.currentSampleRateIndex)
			if retval == 1:
				return True #The DLL documentation may contain a typo on the return val.
			else:
				return False
				
	
	def convertReadData(self, inputData, scale, scalePoints=32.0):
		"""Helper function for converting the data taken from the scope into its true analog representation.
		Takes input from scope data, and the scaling factor, with the optional number of points in the scaling division.
		Returns an array of analog values read from the scope."""
		pointDiv = scale/scalePoints
		out = [0.0 for i in inputData]
		#inputData = [i.value for i in inputData]
		for i in xrange(0, len(inputData)):
			out[i] = inputData[i] * pointDiv
		return out
	
	def readDataFromScope(self, dataPoints=500, dispPoints=500):
		"""Takes two optional arguments, number of data points and number of display point
			to grab. Returns a tuple with channel 1 data, channel 2 data, time since capture init, and a trigger index on success, and None on failure."""
		if self.calData == None:
			return None
		else:
			dataCH1 = (c_short * dataPoints)()
			dataCH2 = (c_short * dataPoints)()
		
			t_index = c_ulong(0)
		
			retval = self.marchdll.dsoReadHardData(self.scopeid,
												byref(dataCH1),
												byref(dataCH2),
												c_ulong(dataPoints),
												byref(self.calData),
												self.currentVoltIndex[1],
												self.currentVoltIndex[2],
												self.currentTriggerSweep,
												self.currentTriggerSource,
												self.currentTriggerLevel,
												self.currentTriggerSlope,
												self.currentSampleRateIndex,
												self.currentHTriggerPosition,
												c_ulong(dispPoints),
												byref(t_index),
												self.currentDValueMode)
			if retval == -1:
				return None
			else:
				return (self.convertReadData(dataCH1, self.currentVoltDiv[1]), self.convertReadData(dataCH2, self.currentVoltDiv[2]), [ i/1e6 for i in range(0, dataPoints)], t_index)
				
	def setupDsoCalLevel(self):
		"""This function takes no arguments, and returns true on success, false on failure.
			This is used to poll the oscilloscope's calibration level."""
		if self.calData == None:
			self.calData = (c_short * 32)()
		retval = self.marchdll.dsoGetCalLevel(self.scopeid, byref(self.calData), c_short(32))
		if retval == 0:
			return True
		else:
			print "setupDsoCalLevel retval: ", retval
			return False
			
	def calibrateDso(self):
		"""This function takes no arguments, and returns true on success, false on failure.
			This is used to set the oscilloscope's calibration level."""
		if self.calData == None:
			self.calData = (c_short * 32)()
		retval = self.marchdll.dsoCalibrate(self.scopeid, self.currentSampleRateIndex, 
											self.currentVoltIndex[1], self.currentVoltIndex[2],
											byref(self.calData))
		if retval == 0:
			return True
		else:
			return False
			
	def getCalibrationData(self):
		"""This function takes no arguments, and returns the current state of calibration data.
			If None is returned, no calibration settings were loaded. This could be called after the calibrateDso function."""
		return self.calData
		
	def setDsoCalibration(self, calData):
		"""This function takes one argument and returns True on success, False on failure.
			The argument is a previous calibration to be loaded to the device. This function sets
			the calibration level."""
		if type(calData) is not type((c_short*32)()):
			return False
		else:
			self.calData = calData
			retval = self.marchdll.dsoSetCalLevel(self.scopeid, byref(self.calData), 32)
			if retval == 0:
				return True
			else:
				return False
											
												
		
#Run these unit tests to make sure the API works correctly.				
if __name__ == "__main__":
	scope = oscilloscope()
	print "Running Unit tests..."
	print "Test 1 -> Test Device Attached function."
	print scope.isAttached(), "<-should be true if a scope is attached."
	print oscilloscope(scopeid=1).isAttached(), "<-should be false if 1 or less scopes are attached."
	print
	print "Valid Voltage Division settings:", scope.getVoltageDivDict()
	print
	print "Valid Channels", scope.getChannelsDict()
	print
	print "Valid Sampling Rate,", scope.getSampleRateDict()
	print
	print scope.setVoltageDivision(100, 200), "<-should return false."
	print scope.setVoltageDivision(1, 6), "<-should return true."
	print scope.setSamplingRate(500), "<-should return false."
	print scope.setSamplingRate(25), "<-should return true."
	print scope.readDataFromScope(), "<-should return None."
	print scope.setupDsoCalLevel(), "<-should return True."
	calLevel = scope.getCalibrationData()
	print "Loaded calibration level:", [int(i) for i in calLevel]
	print scope.setDsoCalibration(calLevel), "<-should return True."
	print "\n------------------\n\tData Tests\t\n------------------\n"
	print "\tVolt Div == 2.0 V, Sample Rate = 500 KSa/s\n"
	print "------------------\n"
	data =  scope.readDataFromScope()
	for entry in data:
		print entry, "\n------------------"
	print "\n------------------\n"
	print "\tVolt Div == 0.5 V, Sample Rate = 200 KSa/s\n"
	print "------------------\n"
	scope.setSamplingRate(26)
	scope.setVoltageDivision(1, 4)
	data =  scope.readDataFromScope()
	for entry in data:
		print entry, "\n------------------"
#!/usr/local/bin/python3
#NOTE TO SELF... GitSavvy => Shift Command P, then "git:add", "git:commit", "git:push"...
#... shortcut keys - refer to https://github.com/divmain/GitSavvy/issues/222
#... "pip install <la da>" => "sudo -H pip3 install <la da>"
import sys
import time
import threading
import socket
import io
import json
import avro.datafile
import avro.schema
import avro.io
import tkinter
import datetime
from enum import Enum

def Main():
	global BackgroundRunning
	global DataTapStatus
	#I - Set up program operation
	# A - set up communications with IbDataTap
	ReadSchemas()
	PrepareConnectionParameters()
	# B - set up program termination
	PrepareProgramEnd()
	# C - set up disk storage parameters
	PrepareDiskStorage()
	# D - determine the list of expiration dates of interest
	# E - connect to TWS
	# F - start underlying monitor
	#II - Gather the day's data
	# A - initialize a list (initially empty) of ongoing monitors
	# B - initialize a list (initially empty) of strike prices of interest
	# C - set up background thread to perform "E" below
	# D - start GUI to make state and activity visible
	# E - loop periodically:
	#  1 - check current underlying value
	#  2 - include on the list of strike prices of interest:
	#   a - the strike price closest to the underlying price
	#   b - the ten next strike prices above that closest strike price
	#   c - the ten next strike prices below that closest strike price
	#  3 - include on the list of ongoing monitors:
	#   a - call options for all expiration dates and strike prices of interest
	#   a - put options for all expiration dates and strike prices of interest
	#  4 - for each monitor on the ongoing list, start a thread to:
	#   a - start an IbDataTap monitor for that right/strike/expiration
	#   b - periodically send a read request for that monitor
	#   c - receive, parse, format and store to disk the read response
	#  5 - check current performance measures:
	#   a - # of active threads
	#   b - CPU loading
	#   c - mean time between monitor read request send and receipt of monitor read response
	#III - Close down program operation
	# A - signal all monitor threads to close down
	# B - wait 'till all monitor threads are closed
	# C - close down TWS connection
	# D - terminate program

	BackgroundRunning = True
	DataTapStatus = {
		"MarketDataTiming": "NotSpecified",
		"TwsPreferredClientId": 0,
		"TwsPortNumber": 0,
		"ConnectionStatus": "NotSpecified",
		"NumberOfMonitorsOnList": 0,
		"DiagnosticInteger": 0
	}
	MonitorManagerThr = threading.Thread(target=MonitorManagerThread)
	MonitorManagerThr.start()
	PrepareGui()
	UpdateGui()

	#Debug!!!
	GetDataTapStatus()
#	GuiWindow.mainloop()
	#Debug!!!

	BackgroundRunning = False

def ReadSchemas():
	global CancelMonitorRequestWriterSchema
	global CancelMonitorResultReaderSchema
	global CommandAcknowledgementReaderSchema
	global ControlCommandWriterSchema
	global MonitorDataReaderSchema
	global ReadMonitorRequestWriterSchema
	global StartContractMonitorRequestWriterSchema
	global StartMonitorResultReaderSchema
	global StartUnderlyingMonitorRequestWriterSchema
	global StatusReportReaderSchema
	CancelMonitorRequestWriterSchema = avro.schema.Parse(open("schemas/CancelMonitorRequestWriterSchema.txt").read())
	CancelMonitorResultReaderSchema = avro.schema.Parse(open("schemas/CancelMonitorResultReaderSchema.txt").read())
	CommandAcknowledgementReaderSchema = avro.schema.Parse(open("schemas/CommandAcknowledgementReaderSchema.txt").read())
	ControlCommandWriterSchema = avro.schema.Parse(open("schemas/ControlCommandWriterSchema.txt").read())
	MonitorDataReaderSchema = avro.schema.Parse(open("schemas/MonitorDataReaderSchema.txt").read())
	ReadMonitorRequestWriterSchema = avro.schema.Parse(open("schemas/ReadMonitorRequestWriterSchema.txt").read())
	StartContractMonitorRequestWriterSchema = avro.schema.Parse(open("schemas/StartContractMonitorRequestWriterSchema.txt").read())
	StartCMonitorResultReaderSchema = avro.schema.Parse(open("schemas/StartMonitorResultReaderSchema.txt").read())
	StartUnderlyingMonitorRequestWriterSchema = avro.schema.Parse(open("schemas/StartUnderlyingMonitorRequestWriterSchema.txt").read())
	StatusReportReaderSchema = avro.schema.Parse(open("schemas/StatusReportReaderSchema.txt").read())

def PrepareConnectionParameters():
	global TwsClientId
	global TwsConnectionPortNumber
	global TwsMarketDataTiming
	global DataTapIpAddress
	global DataTapIpPortNumber

	DefaultTwsClientId = 1
	DefaultTwsConnectionPortNumber = 7496
	DefaultTwsMarketDataTiming = "Live"
	LocalIpAddress = "192.168.1.45"
	DistantIpAddress = "73.254.166.172"
	DefaultIpPortNumber = 56781

	TwsClientId = DefaultTwsClientId
	TwsConnectionPortNumber = DefaultTwsConnectionPortNumber
	TwsMarketDataTiming = DefaultTwsMarketDataTiming
	DataTapIpAddress = LocalIpAddress
	DataTapIpPortNumber = DefaultIpPortNumber

def	PrepareProgramEnd():
	global TodayDateTime
	global TodayDateString
	global TodayYear
	global TodayYearString
	global TodayMonth
	global TodayMonthString
	global TodayDay
	global TodayDayString
	global StartTime
	global StartTimeString
	global StartHour
	global StartHourString
	global StartMinute
	global StartMinuteString
	global StartSecond
	global StartSecondString
	global TimeToEndBackground
	global TimeToEndGui

	TodayDate = datetime.date.today()
	TodayYear = TodayDate.year
	TodayYearString = format(TodayYear, '4d')
	TodayMonth = TodayDate.month
	TodayMonthString = format(TodayMonth, '2d')
	TodayDay = TodayDate.day
	TodayDayString = format(TodayDay, '2d')
	TodayDateString = TodayYearString + "-" + TodayMonthString + "-" + TodayDayString
	StartTime = datetime.datetime.now()
	StartHour = StartTime.hour
	StartHourString = format(StartHour, '02d')
	StartMinute = StartTime.minute
	StartMinuteString = format(StartMinute, '02d')
	StartSecond = StartTime.second
	StartSecondString = format(StartSecond, '02d')
	StartTimeString = StartHourString + ":" + StartMinuteString + ":" + StartSecondString
	TimeToEndBackground = StartTime + datetime.timedelta(hours=10)
	TimeToEndGui = StartTime + datetime.timedelta(hours=10, minutes=30)

def	PrepareDiskStorage():
	global ExecutionPath
	global DataStoragePath

def PrepareGui():
	global GuiWindow
	global GuiMessageLabel
	global GuiThreadCountLabel
	global GuiDataTapStatusText
	global GuiExitButton
	global GuiTestButton
	GuiWindow = tkinter.Tk()
	GuiWindow.geometry("800x600+100+100")
	GuiWindow.configure(background="cyan")
	GuiWindow.resizable(True, True)
	GuiMessageLabel = tkinter.Label(GuiWindow, text="Initial GuiMessageLabel text",
												fg="red", bg="green",
												font=("Arial","20","italic"),
												relief="sunken")
	GuiMessageLabel.place(anchor="nw", relx=0.1,rely=0.9,relwidth=0.7, relheight=0.07)
	GuiThreadCountLabel = tkinter.Label(GuiWindow, text="Thread count:")
	GuiThreadCountLabel.place(anchor="nw", relx=0.1, rely=0.1)
	GuiDataTapStatusText = tkinter.Text(GuiWindow, height=6, width=50)
	GuiDataTapStatusText.place(anchor="w", relx=0.1, rely=0.5)
	GuiExitButton = tkinter.Button(GuiWindow, text="Exit", command=ExitGui)
	GuiExitButton.place(anchor="se", relx=0.95, rely=0.95)
	GuiTestButton = tkinter.Button(GuiWindow, text="Test", command=TestFunction)
	GuiTestButton.place(anchor="sw", relx=0.03, rely=0.95)

def TestFunction():
	GetDataTapStatus()

def UpdateGui():
	GuiDataTapStatusText.delete("1.0", "end")
	GuiDataTapStatusText.insert("end", "MarketDataTiming: " + DataTapStatus["MarketDataTiming"] +
									"\nTwsPreferredClientId: " + str(DataTapStatus["TwsPreferredClientId"]) +
									"\nTwsPortNumber: " + str(DataTapStatus["TwsPortNumber"]) +
									"\nConnectionStatus: " + DataTapStatus["ConnectionStatus"] +
									"\nNumberOfMonitorsOnList: " + str(DataTapStatus["NumberOfMonitorsOnList"]) +
									"\nDiagnosticInteger: " + str(DataTapStatus["DiagnosticInteger"]))
	GuiThreadCountLabel.configure(text="Thread count: " + str(threading.active_count()))
	if datetime.datetime.now() > TimeToEndGui:
		GuiWindow.destroy()
	else:
		GuiWindow.after(1000, UpdateGui)

def ExitGui():
	global BackgroundRunning
	BackgroundRunning = False
	GuiWindow.destroy()

def MonitorManagerThread():
	global BackgroundRunning
	UnderlyingThread = threading.Thread(target=MonitorUnderlyingThread)
	UnderlyingThread.start()
	while BackgroundRunning:
		if datetime.datetime.now() > TimeToEndBackground:
			BackgroundRunning = False
		else:
			# ContractDescriptorArray = 
			time.sleep(2.0)

def MonitorUnderlyingThread(symbol="SPX", type="IND"):
	while BackgroundRunning:
		time.sleep(2.0)

def MonitorContractThread(MyContract):
	MyStrikePrice = MyContract.MyStrikePrice
	MyExpiration = MyContract.Expiration
	MyRight = MyContract.Right
	while BackgroundRunning:
			time.sleep(0.5)

def TestButtonClick():
	print("Clicked")

class SessionType(Enum):
	NotSpecified = 0
	StatusControl = 1
	Monitor = 2

class PacketTask(Enum):
	NotSpecified = 0
	ReadStatus = 1
	ControlCommand = 2
	CommandAcknowledge = 3
	StartUnderlying = 4
	StartOption = 5
	ReadMonitor = 6
	CancelMonitor = 7
	EndSession = 8

class OperatingModes(Enum):
	Development = 0
	Production = 1

class StartRequestResultReturnCode(Enum):
	NotSpecified = 0
	Success = 1
	IdAlreadyInUse = 2
	UnableToConnectToIB = 3

class CancelRequestResultReturnCode(Enum):
	NotSpecified = 0
	Success = 1
	IdNotFound = 2

class RequestedMonitorStatus(Enum):
	NotSpecified = 0
	Pending = 1
	Active = 2
	RejectedByIB = 3

class ReadRequestResultReturnCode(Enum):
	NotSpecified = 0
	Success = 1
	IdNotOnActiveList = 2

class CommandType(Enum):
	NotSpecified = 0
	SetConnectionParameters = 1
	ConnectToTws = 2
	DisconnectFromTws = 3

class MarketDataTimingType(Enum):
	NotSpecified = 0
	Live = 1
	Frozen = 2
	Delayed = 3
	DelayedFrozen = 4

class ConnectionStatus(Enum):
	NotSpecified = 0
	ConnectionAttemptFailed = 1
	Connected = 2
	ConnectionClosed = 3

class ExpirationDateClass(dict):
	def __init__(self, *args, **kwargs):
		self['year'] = 1
		self['month'] = 1
		self['day'] = 2016

class StartContractMonitorRequestClass(dict):
	def __init__(self, *args, **kwargs):
		ed = ExpirationDateClass()
		self['Symbol'] = ''
		self['ExpirationDate'] = ed
		self['ContractRight'] = ''
		self['StrikePrice'] = 1.0
		self['RequestedSubscriptionId'] = 0

class StartMonitorResultClass(dict):
	def __init__(self, *args, **kwargs):
		self['RequestSuccessCode'] = StartRequestResultReturnCode['NotSpecified'].name
		self['RequestErrorMessage'] = ''
		self['AssignedSubscriptionId'] = 0
		self['ThisIsTheUnderlying'] = False

class CancelMonitorRequestClass(dict):
	def __init__(self, *args, **kwargs):
		self['SubscriptionIdToCancel'] = 0

class CancelMonitorResultClass(dict):
	def __init__(self, *args, **kwargs):
		self['RequestSuccessCode'] = CancelRequestResultReturnCode['NotSpecified'].name
		self['SubscriptionId'] = 0

class ReadMonitorRequestClass(dict):
	def __init__(self, *args, **kwargs):
		self['SubscriptionIdToRead'] = 0
		self['SequenceNumber'] = 0

class OptionCompStructureClass(dict):
	def __init__(self, *args, **kwargs):
		self['Price'] = 0.0
		self['Size'] = 0
		self['ImpliedVolatility'] = 0.0
		self['Delta'] = 0.0
		self['Theta'] = 0.0
		self['Gamma'] = 0.0
		self['Vega'] = 0.0

class MonitorDataClass(dict):
	def __init__(self, *args, **kwargs):
		ed = ExpirationDateClass()
		aoc = OptionCompStructureClass()
		boc = OptionCompStructureClass()
		loc = OptionCompStructureClass()
		moc = OptionCompStructureClass()
		self['MonitorStatus'] = RequestedMonitorStatus['].NotSpecified'].name
		self['RequestSuccessCode'] = ReadRequestResultReturnCode['NotSpecified'].name
		self['SequenceNumber'] = 0
		self['MonitorStartMilliseconds'] = 0
		self['MonitorLastUpdateMilliseconds'] = 0
		self['MonitorUpdateCount'] = 0
		self['Symbol'] = ''
		self['ExpirationDate'] = ed
		self['ContractRight'] = ''
		self['StrikePrice'] = 0.0
		self['SubscriptionId'] = 0
		self['Ask'] = aoc
		self['Bid'] = boc
		self['Last'] = loc
		self['Model'] = moc
		self['Volume'] = 0
		self['TimeStamp'] = ''
		self['Open'] = 0.0
		self['High'] = 0.0
		self['Low'] = 0.0
		self['Close'] = 0.0

class StartUnderlyingMonitorRequestClass(dict):
	def __init__(self, *args, **kwargs):
		self['Symbol'] = ''
		self['SymbolType'] = ''
		self['RequestedSubscriptionId'] = 0


class ControlCommandClass(dict):
	def __init__(self, *args, **kwargs):
		self['Command'] = CommandType['NotSpecified'].name
		self['IntegerParameter'] = 0
		self['IntegerParameter2'] = 0
		self['LongParameter'] = 0
		self['DoubleParameter'] =  0.0
		self['BoolParameter'] = False
		self['StringParameter'] = ''
		self['MarketDataType'] = MarketDataTimingType['NotSpecified'].name

class CommandAcknowledgementClass(dict):
	def __init__(self, *args, **kwargs):
		self['SubscriptionId'] = 0

class StatusReportClass(dict):
	def __init__(self, *args, **kwargs):
		self['MarketDataType'] = MarketDataTimingType['NotSpecified'].name
		self['TwsPreferredCliendId'] = 0
		self['TwsPortNumber'] = 0
		self['IbConnectionStatus'] = ConnectionStatus['NotSpecified'].name
		self['NumberOfIdsOnMonitorList'] = 0
		self['DiagnosticInteger'] = 0


def ConnectToTws():
	try:
		OutgoingBuffer = io.BytesIO()
		PhonyCommand = {'Command':CommandType['ConnectToTws'].name,
						'IntegerParameter':1,
						'IntegerParameter2':7438,
						'LongParameter':123,
						'DoubleParameter':2.0,
						'BoolParameter':True,
						'StringParameter':'Hi!',
						'MarketDataType':MarketDataTimingType['Live'].name}
		AvroSerializationBuffer = io.BytesIO()
		writer = avro.datafile.DataFileWriter(AvroSerializationBuffer, avro.io.DatumWriter(), ControlCommandWriterSchema)
		writer.append(PhonyCommand)
		writer.flush()
		AvroSerializationBuffer.seek(0)
		PacketDataBuffer = io.BytesIO()
		PacketDataBuffer = AvroSerializationBuffer.read()
		PacketLengthBuffer = (16 + len(PacketDataBuffer)).to_bytes(8, byteorder='little')
		SessionTypeBuffer = (SessionType['StatusControl'].value).to_bytes(4, byteorder='little')
		PacketTaskBuffer = (PacketTask['ControlCommand'].value).to_bytes(4, byteorder='little')
		OutgoingBuffer = PacketLengthBuffer + SessionTypeBuffer + PacketTaskBuffer + PacketDataBuffer
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((DataTapIpAddress, DataTapIpPortNumber))
		s.send(OutgoingBuffer)
		PacketLength = s.recv(8)
		ReceivedSessionType = s.recv(4)
		ReceivedPacketTask = s.recv(4)
		IncomingPacket = s.recv(1024)
		IncomingAvro = IncomingPacket
		ByteBufferAvro = io.BytesIO(IncomingAvro)
		reader = avro.datafile.DataFileReader(ByteBufferAvro, avro.io.DatumReader())
		for datum in reader:
			print('datum: ' + str(datum))
			print('datum[SubscriptionId]: ' + str(datum['SubscriptionId']))
		reader.close()
		s.close()

	except Exception as e:
		LogError('Exception in ConnectToTws: ' + str(e))

def GetDataTapStatus(): 
	#DevNote: the TCP packet for "readstatus" is 16 bytes long:
	# first 8 bytes are the total packet length: 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
	# the second 4 bytes are the "SessionType" (StatusControl): 0x01, 0x00, 0x00, 0x00
	# and the last 4 bytes are the "PacketTask" (ReadStatus): 0x01, 0x00, 0x00, 0x00
	# making the entire TCP frame on the wire: 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00
	#This is the minimum length a TCP/IP packet to or from the IbDataLink can be: 8 bytes giving
	# total packet length, 4 bytes encoding the session type and 4 bytes encoding the
	# packet task (which is essentially a session sub-type). The length of the "packet
	# contents" in this case is zero. The response containing the status report has
	# all 16 of the above bytes PLUS a packet content of the AVRO-serialized status report
	# so it has a total length of 23 bytes.
	global GuiMessageLabel
	try:
		OutgoingBuffer = io.BytesIO()

		# # #Make a phony avro-serialized packet content with a command
		# PhonySchema = avro.schema.Parse(json.dumps({
		# 	"namespace"		: "example.avro",
		# 	"type"			: "record",
		# 	"name"			: "User",
		# 	"fields"		: [
		# 		{"name": "name"				, "type": "string"},
		# 		{"name": "favorite_number"	, "type": ["int", "null"]},
		# 		{"name": "favorite_color"	, "type": ["string", "null"]},
		# 	 	{"name":"Command","type":{"type":"enum",
 	# 										"name":"IbData.CommandType",
 	# 										# "name":"CommandType",
 	# 										# "namespace":"IbData",
 	# 										"symbols":["NotSpecified",
 	# 												"SetConnectionParameters",
 	# 												"ConnectToTws",
 	# 												"DisconnectFromTws"]}}
		# 		# {"name": "Command"			, "type":
		# 		# 		{"type":"enum",
		# 		# 			"name":"IbData.CommandType",
		# 		# 			"symbols":["NotSpecified",
		# 		# 						"SetConnectionParameters",
		# 		# 						"ConnectToTWS",
		# 		# 						"DisconnectFromTWS"]}}
		# 	]
		# 	}))
		# AvroSerializationBuffer = io.BytesIO()
		# PhonyCommand = {'name': 'Eli', 'favorite_number': 42, 'favorite_color': 'black', 'Command': CommandType['NotSpecified'].name}
		# writer = avro.datafile.DataFileWriter(AvroSerializationBuffer, avro.io.DatumWriter(), PhonySchema)


		PhonyCommand = ControlCommandClass()
		PhonyCommand.Command = CommandType['ConnectToTws'].name
		# PhonyCommand = {'Command':CommandType['ConnectToTws'].name,
		# 				'IntegerParameter':2,
		# 				'IntegerParameter2':7438,
		# 				'LongParameter':123,
		# 				'DoubleParameter':2.0,
		# 				'BoolParameter':True,
		# 				'StringParameter':'Hi!',
		# 				'MarketDataType':MarketDataTimingType['Live'].name}
		AvroSerializationBuffer = io.BytesIO()
		# writer = avro.datafile.DataFileWriter(AvroSerializationBuffer, avro.io.DatumWriter(), json.dumps(ControlCommandWriterSchema))
		writer = avro.datafile.DataFileWriter(AvroSerializationBuffer, avro.io.DatumWriter(), ControlCommandWriterSchema)

		# PhonySchema = avro.schema.Parse(json.dumps({
		# 	"namespace"		: "example.avro",
		# 	"type"			: "record",
		# 	"name"			: "User",
		# 	"fields"		: [
		# 		{"name": "long"				, "type": "long"},
		# 	 	{"name": "bool"				, "type": "boolean"},
		# 	 	# {"name": "float"			, "type": "float"},
		# 	 	{"name": "double"			, "type": "double"},
		# 		{"name": "string"			, "type": "string"},
		# 		{"name": "integer"			, "type": "int"}
		# 	]
		# 	}))
		# AvroSerializationBuffer = io.BytesIO()
		# # PhonyCommand = {'string': 'STRING', 'integer': 42, 'long': 100, 'float': 1.0, 'bool': 1}
		# PhonyCommand = {'long':123, 'bool':True, 'double':2.0, 'string': 'STRING', 'integer': 42}
		# writer = avro.datafile.DataFileWriter(AvroSerializationBuffer, avro.io.DatumWriter(), PhonySchema)

		writer.append(PhonyCommand)
		writer.flush()
		AvroSerializationBuffer.seek(0)
		PacketDataBuffer = io.BytesIO()
		PacketDataBuffer = AvroSerializationBuffer.read()

		# # TCP packet header for Status request
		# PacketLengthBuffer = (16).to_bytes(8, byteorder='little')
		# SessionTypeBuffer = (SessionType['StatusControl'].value).to_bytes(4, byteorder='little')
		# PacketTaskBuffer = (PacketTask['ReadStatus'].value).to_bytes(4, byteorder='little')

		# TCP packet header for 'ConnectToTws' command
		PacketLengthBuffer = (16 + len(PacketDataBuffer)).to_bytes(8, byteorder='little')
		SessionTypeBuffer = (SessionType['StatusControl'].value).to_bytes(4, byteorder='little')
		PacketTaskBuffer = (PacketTask['ControlCommand'].value).to_bytes(4, byteorder='little')




		# OutgoingBuffer = PacketLengthBuffer + SessionTypeBuffer + PacketTaskBuffer
		OutgoingBuffer = PacketLengthBuffer + SessionTypeBuffer + PacketTaskBuffer + PacketDataBuffer

		print("PacketDataBuffer: " + str(PacketDataBuffer))
		# return

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# print("connecting")
		s.connect((DataTapIpAddress, DataTapIpPortNumber))
		# print("sending")
		s.send(OutgoingBuffer)
		# print("updating GUI label")
		# GuiMessageLabel.configure(text="Sent status request to IP address: " + str(DataTapIpAddress) + " using port: " + str(DataTapIpPortNumber))
		# print("receiving")
		PacketLength = s.recv(8)
		print('PacketLength: ' + str(PacketLength))
		ReceivedSessionType = s.recv(4)
		print('SessionType: ' + str(ReceivedSessionType))
		ReceivedPacketTask = s.recv(4)
		print('PacketTask: ' + str(ReceivedPacketTask))
		IncomingPacket = s.recv(1024)
		print("IncomingPacket: ", str(IncomingPacket))
		# IncomingAvro = IncomingPacket[16:]
		IncomingAvro = IncomingPacket
		# print("IncomingAvro: ", str(IncomingAvro))
		ByteBufferAvro = io.BytesIO(IncomingAvro)
		# print("making avro reader")
		reader = avro.datafile.DataFileReader(ByteBufferAvro, avro.io.DatumReader())
		# print("fetching reader contents")
		for datum in reader:
			print('datum: ' + str(datum))
			print('datum[SubscriptionId]: ' + str(datum['SubscriptionId']))
			# print('datum[DiagnosticInteger]: ' + str(datum['DiagnosticInteger']))
			# print('datum[TswPortNumber]: ' + str(datum['TwsPortNumber']))
		# print("closing reader")
		reader.close()
		# print("closing socket")
		s.close()
	except Exception as e:
		print("Exception in GetDataTapStatus(): " + str(e))
	else:
		print("try-else in GetDataTapStatus()")
	finally:
		print("try-finally in GetDataTapStatus()")

def LogError(message):
	print(message)

if __name__ == '__main__':
	Main()

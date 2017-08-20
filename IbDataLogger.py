#!/usr/local/bin/python3
#NOTE TO SELF... GitSavvy => Shift Command P, then "git:add", "git:commit", "git:push"...
#... shortcut keys - refer to https://github.com/divmain/GitSavvy/issues/222
import sys
import time
import threading
import socket
import avro
import avro.schema
import avro.io
import tkinter
import datetime

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
	GuiWindow.mainloop()
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
	CancelMonitorRequestWriterSchema = avro.schema.parse(open("schemas/CancelMonitorRequestWriterSchema.txt").read())
	CancelMonitorResultReaderSchema = avro.schema.parse(open("schemas/CancelMonitorResultReaderSchema.txt").read())
	CommandAcknowledgementReaderSchema = avro.schema.parse(open("schemas/CommandAcknowledgementReaderSchema.txt").read())
	ControlCommandWriterSchema = avro.schema.parse(open("schemas/ControlCommandWriterSchema.txt").read())
	MonitorDataReaderSchema = avro.schema.parse(open("schemas/MonitorDataReaderSchema.txt").read())
	ReadMonitorRequestWriterSchema = avro.schema.parse(open("schemas/ReadMonitorRequestWriterSchema.txt").read())
	StartContractMonitorRequestWriterSchema = avro.schema.parse(open("schemas/StartContractMonitorRequestWriterSchema.txt").read())
	StartCMonitorResultReaderSchema = avro.schema.parse(open("schemas/StartMonitorResultReaderSchema.txt").read())
	StartUnderlyingMonitorRequestWriterSchema = avro.schema.parse(open("schemas/StartUnderlyingMonitorRequestWriterSchema.txt").read())
	StatusReportReaderSchema = avro.schema.parse(open("schemas/StatusReportReaderSchema.txt").read())

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
	global DataTapStatus
	global GuiWindow
	global GuiDataTapStatusText
	global GuiMessageLabel
	global GuiThreadCountLabel
	global GuiExitButton
	GuiWindow = tkinter.Tk()
	GuiWindow.geometry("800x600+100+100")
	GuiWindow.configure(background="cyan")
	GuiWindow.resizable(True, True)
	GuiDataTapStatusText = tkinter.Text(GuiWindow, height=6, width=50)
	GuiDataTapStatusText.place(anchor="w", relx=0.1, rely=0.5)
	GuiMessageLabel = tkinter.Label(GuiWindow, text="Initial GuiMessageLabel text",
												fg="red", bg="green",
												font=("Arial","20","italic"),
												relief="sunken")
	GuiMessageLabel.place(anchor="nw", relx=0.1,rely=0.9,relwidth=0.7, relheight=0.07)
	GuiThreadCountLabel = tkinter.Label(GuiWindow, text="Thread count:")
	GuiThreadCountLabel.place(anchor="nw", relx=0.1, rely=0.1)
	GuiExitButton = tkinter.Button(GuiWindow, text="Exit", command=ExitGui)
	GuiExitButton.place(anchor="se", relx=0.95, rely=0.95)

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

def GetDataTapStatus():
	if(DistantIpAddress == IpAddress):
		print("Distant Status.")
	else:
		print("Local Status.")

	print ("Sending to IP address: " + str(IpAddress) + " using port: " + str(StatusPortNumber))

	outgoingMessage = bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00])
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((IpAddress, StatusPortNumber))
	s.send(outgoingMessage)
	incomingMessage = s.recv(1024)
	s.close()
	print ("sent: status request to " + IpAddress + ":" + str(StatusPortNumber) + ", received: ")
	for incomingByte in incomingMessage:
		print(format(incomingByte, '02x'), " ", end="")
	print("")
	print("...")

def Boris(IpAddress):
	if(DistantIpAddress == IpAddress):
		print("Distant Boris.")
	else:
		print("Local Boris.")

	print ("Sending to IP address: " + str(IpAddress) + " using port: " + str(BorisPortNumber))

	outgoingMessage = "Boris?"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("0.0.0.0", BorisPortNumber))
	s.connect((IpAddress, BorisPortNumber))
	s.send(outgoingMessage.encode())
	incomingMessage = s.recv(1024).decode()
	print ("sent: " + outgoingMessage + " to " + IpAddress + ":" + str(PortNumber) + ", received: " + incomingMessage)
	s.close()

if __name__ == '__main__':
	Main()

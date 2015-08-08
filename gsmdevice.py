#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008, Daniel Knaggs                                     #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################


import serial

class GSMDevice(object):
	def __init__(self, port, speed, bits, parity, stop, timeout):
		self.ser = serial.Serial()
		self.ser.baudrate = speed
		self.ser.bytesize = bits
		self.ser.parity = parity
		self.ser.port = port
		self.ser.stopbits = stop
		self.ser.timeout = timeout
		
		self.ser.open()
		
	def changeTimeout(self, newtimeout):
		self.ser.timeout = newtimeout
		
	def dispose(self):
		self.ser.close()
		self.ser = None
		
	def getBERPercentage(self, index):
		if index == 0:
			return "< 0.2%"
			
		elif index == 1:
			return "0.2-0.4%"
			
		elif index == 2:
			return "0.4-0.8%"
			
		elif index == 3:
			return "0.8-1.6%"
			
		elif index == 4:
			return "1.6-3.2%"
			
		elif index == 5:
			return "3.2-6.4%"
			
		elif index == 6:
			return "6.4-12.8%"
			
		elif index == 7:
			return "> 12.8%"
			
		elif index == 99:
			return "Not Known"
		
	def receiveChar(self, chars = 1):
		return self.ser.read(chars)
		
	def receiveDualResult(self):
		blank = self.receiveLine()
		ir = self.receiveLine()
		
		blank = self.receiveLine()
		frc = self.receiveLine()
		
		return ir, frc
		
	def receiveLine(self):
		return self.ser.readline().replace("\r", "").replace("\n", "")
		
	def receiveSingleResult(self):
		blank = self.receiveLine()
		frc = self.receiveLine()
		
		
		return frc
		
	def sendATCommand(self, command = "", skipcheck = False, dualcheck = False):
		if skipcheck:
			self.ser.write("AT%s\r" % command)
			
			return True
			
		else:
			self.ser.write("AT%s=?\r" % command.split("=")[0].replace("?", ""))
			
			if not dualcheck:
				if self.receiveSingleResult() == "OK":
					self.ser.write("AT%s\r" % command)
					
					return True
					
				else:
					return False
				
			else:
				ir, frc = self.receiveDualResult()
				
				if frc == "OK":
					self.ser.write("AT%s\r" % command)
					
					return True
					
				else:
					return False
			
		
	def sendRawCommand(self, command, newline = True):
		self.ser.write(command)
		
		if newline:
			self.ser.write("\r")
	
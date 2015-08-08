#!/usr/bin/env python

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


############################
# GSMSMS                   #
############################
# Version:	v0.2.1     #
############################


import getopt
from gsmdevice import GSMDevice
import sys


gsm = None

gsm_bits = 8
gsm_parity = "N"
gsm_port = "/dev/cuad0"
gsm_speed = 115200
gsm_stop_bits = 1


# Constants
VERSION = "0.2.1"


def exitProgram():
	global gsm
	
	
	if gsm <> None:
		gsm.dispose()
		gsm = None
	
	sys.exit()
	
def iif(testval, trueval, falseval):
	if testval:
		return trueval
	
	else:
		return falseval
	
def main():
	global gsm, gsm_port, gsm_speed
	
	
	minimum_signal_strength = 5
	
	sim_pin = ""
	
	sms_to = ""
	sms_to_method = 0
	sms_message = ""
	sms_method = 0
	
	
	# Show the copyright notice first
	print """
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

WARNING: If you do not agree to the above copyright/license notice, cease using the software immediately and remove from your system.
"""

	# Welcome message
	print ""
	print ""
	print "Information: Welcome to GSMSMS v%s." % VERSION
	print "Information: Please report any bugs you find so I can fix them!"
	print ""
	
	# Parse any arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "g:h:m:n:p:s:t:")
		
		if len(opts) == 0:
			print "Usage: sendsms.py -n \"+447912345678\" -m \"Hello\" -p 1234 -t 5 -h 0 -g /dev/cuad0 -s 115200."
			print "       -n: Number in ISDN ITU E.164/E.163 format - REQUIRED"
			print "       -m: Message in double quotes - REQUIRED"
			print "       -p: PIN number for SIM - optional (default: <BLANK>)"
			print "       -t: Minimum signal strength needed to send SMS in dBm - optional (default: 5)"
			print "       -h: Method to send SMS 0 = Send straight away, and 1 = Store message then send from storage - optional (default: 0)"
			print "       -g: COM port which the GSM modem is on - optional (default: /dev/cuad0)"
			print "       -s: COM port speed - optional (default: 115200)"
			
			exitProgram()
			
		else:
			for opt in opts:
				if opt[0] == "-g":
					gsm_port = opt[1]
					
				if opt[0] == "-h":
					sms_method = int(opt[1])
					
				if opt[0] == "-m":
					sms_message = opt[1]
					
				if opt[0] == "-n":
					sms_to = opt[1]
					
				if opt[0] == "-p":
					sms_pin = opt[1]
					
				if opt[0] == "-s":
					gsm_speed = int(opt[1])
					
				if opt[0] == "-t":
					minimum_signal_strength = int(opt[1])
		
	except getopt.error, msg:
		print msg
		sys.exit(1)
	
	
	# Make sure we have everything we need before continuing
	if sms_to == "":
		print "Error: No SMS number has been defined."
		exitProgram()
		
	if sms_message == "":
		print "Error: No SMS message has been defined."
		exitProgram()
		
	else:
		if len(sms_message) > 140:
			print "Error: The SMS message is greater than 140 characters, please shorten the message and try again."
			exitProgram()
			
	if sms_method < 0 or sms_method > 1:
		print "Error: Unknown SMS sending method."
		exitProgram()
		
	if sms_to.startswith("+"):
		sms_to_method = 0
		
		print "Information: Number identified as ISDN ITU E.164/E.163."
		
	else:
		sms_to_method = 1
		
		print "Information: Number identified NOT as ISDN ITU E.164/E.163."
	
	
	
	# Setup the modem
	print "Information: Connecting to GSM modem..."
	
	gsm = GSMDevice(gsm_port, gsm_speed, gsm_bits, gsm_parity, gsm_stop_bits, 1)
	
	# Connect to modem and ensure it's responding
	gsm.sendATCommand(skipcheck = True)
	frc = gsm.receiveSingleResult()
	
	if frc == "OK":
		# Modem is ready, re-setup...
		print "Information: GSM modem responded."
		
		if gsm.sendATCommand("E0", skipcheck = True):
			print "Information: Checking if we need a PIN..."
			
			if gsm.sendATCommand("+CPIN?"):
				ir, frc = gsm.receiveDualResult()
				
				# Check if we need a PIN
				if ir == "+CPIN: SIM PIN":
					# PIN code needed, so send it
					print "Information: PIN needed, sending..."
					
					gsm.sendATCommand("+CPIN=\"%s\"" % sim_pin, False)
					ir, frc = gsm.receiveDualResult()
					
					if frc == "OK":
						print "Information: PIN accepted."
						
					else:
						print "Error: PIN not accepted."
						
						exitProgram()
						
				elif ir == "+CPIN: SIM PUK":
					print "Warning: SIM card is asking for PUK code."
					
				elif ir == "+CPIN: SIM PUK2":
					print "Warning: SIM card is asking for PUK2 code."
					
				elif ir == "+CPIN: READY":
					print "Information: No PIN required."
					
				else:
					print "Warning: Unexpected response '%s'." % frc
					
				
				
				# Get the network we're on
				print "Information: Determining network..."
				
				if gsm.sendATCommand("+COPS?", True):
					ir, frc = gsm.receiveDualResult()
					
					
					if frc == "OK":
						print "Information: Network is %s." % ir.split(": ")[1].split(",")[2].replace("\"", "")
						
					else:
						print "Warning: Unable to get the network, command may not be supported."
						
				else:
					print "Warning: +COPS command not recognised, unable to get the network."
				
				
				# Get the signal strength, if it's too low we may not want to send it
				print "Information: Determining signal strength..."
				
				if gsm.sendATCommand("+CSQ", dualcheck = True):
					ir, frc = gsm.receiveDualResult()
					
					
					if frc == "OK":
						csq = ir.split(": ")[1].split(",")
						dbm = int(csq[0])
						ber = int(csq[1])
						
						
						print "Information: Signal strength is %ddBm with a BER of '%s'." % (dbm, gsm.getBERPercentage(ber).lower())
						
						if dbm < minimum_signal_strength:
							print "Error: Signal strength is NOT acceptable (needed >= %ddBm), aborting..." % minimum_signal_strength
							
							exitProgram()
						
					else:
						print "Warning: Unable to get the signal strength, command may not be supported."
						
				else:
					print "Warning: +CSQ command not recognised, unable to get the signal strength."
				
				
				# Make sure we have SMS commands available
				print "Information: Determining SMS capabilities..."
				
				if gsm.sendATCommand("+CSMS?", dualcheck = True):
					print "Information: Setting modem to TEXT mode..."
					
					if gsm.sendATCommand("+CMGF=1", dualcheck = True):
						frc = gsm.receiveSingleResult()
						
						if frc == "OK":
							if gsm.sendATCommand("+CSCA?"):
								print "Information: Checking for SMS messaging centre number..."
								
								ir, frc = gsm.receiveDualResult()
								
								if frc == "OK":
									print "Information: Messaging centre is %s." % ir.split(": ")[1].split(",")[0].replace("\"", "")
									
								else:
									print "Warning: Unable to retreive the messaging centre number."
									
								
								print "Information: Sending SMS via +CMGW..."
								
								if sms_method == 0:
									# Send straight away
									if gsm.sendATCommand("+CMGS=\"%s\",%d" % (sms_to, iif(sms_to_method == 0, 145, 129)), True, dualcheck = True):
										# Type the message
										gsm.receiveChar(2)
										gsm.sendRawCommand("%s" % sms_message, False)
										gsm.sendRawCommand(chr(26), False)
										
										gsm.changeTimeout(30)
										
										ir, frc = gsm.receiveDualResult()
										
										if frc == "OK":
											print "Information: SMS has been sent - %s." % ir
											
										else:
											print "Error: SMS has failed to be sent."
											
											exitProgram()
											
									else:
										print "Error: +CMGS command not recognised, we don't have the commands needed to handle SMS."
									
								elif sms_method == 1:
									# Store in memory then send
									if gsm.sendATCommand("+CMGW=\"%s\",%d,\"STO UNSENT\"" % iif(sms_to_method == 0, 145, 129)):
										# Type the message
										gsm.receiveChar(2)
										gsm.sendRawCommand("%s" % sms_message, False)
										gsm.sendRawCommand(chr(26), False)
										
										ir, frc = gsm.receiveDualResult()
										
										if frc == "OK":
											index = int(ir.split(": ")[1])
											
											print "Information: Message stored in memory index %d." % index
											print "Information: Sending SMS from storage..."
											
											gsm.changeTimeout(30)
											
											if gsm.sendATCommand("+CMSS=%d" % index):
												ir, frc = gsm.receiveDualResult()
												
												if frc == "OK":
													print "Information: SMS has been sent - %s." % ir
													print "Information: Erasing message from storage..."
													
													gsm.changeTimeout(1)
													
													if gsm.sendATCommand("+CMGD=%d" % index, dualcheck = True):
														frc = gsm.receiveSingleResult()
														
														if frc == "OK":
															print "Information: Erase successful."
															
														else:
															print "Warning: Erase was NOT successful."
														
													else:
														print "Warning: +CMGD command not recognised, we don't have the commands needed to erase message from memory."
													
												else:
													print "Error: SMS has failed to be sent."
													
													exitProgram()
													
											else:
												print "Error: The message has failed to get saved into memory."
												
												exitProgram()
											
										else:
											print "Error: The message has failed to get saved into memory."
											
											exitProgram()
											
										
									else:
										print "Error: +CMGW command not recognised, we don't have the commands needed to handle SMS."
								
							else:
								print "Error: +CSCA command not recognised, we don't have the commands needed to handle SMS."
								
						else:
							print "Error: Unable to enter TEXT mode for sending SMS."
							
					else:
						print "Error: +CMGF command not recognised, we don't have the commands needed to handle SMS."
						
				else:
					print "Error: +CSMS command not recognised, we don't have the commands needed to handle SMS."
					
			else:
				print "Error: +CPIN command not recognised, please ensure we're talking to a GSM modem."
				
		else:
			print "Error: E0 command not recognised, please ensure we're talking to a GSM modem."
		
	else:
		print "Error: The modem doesn't appear to be ready.  Please ensure you have selected the correct COM port and settings."
	
	# Disconnect
	print "Information: Cleaning up..."
	
	exitProgram()
	


###############################
# Trigger the main subroutine #
###############################
if __name__ == "__main__":
	main()

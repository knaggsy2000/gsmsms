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
import smtplib
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
	
	
	email_from = ""
	email_gateway = ""
	email_to = ""
	
	minimum_signal_strength = 5
	
	sim_pin = ""
	
	
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
	print "Information: Welcome to Receive SMS (GSMSMS v%s)." % VERSION
	print "Information: Please report any bugs you find so I can fix them!"
	print ""
	
	# Parse any arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "e:f:g:m:p:s:t:")
		
		if len(opts) == 0:
			print "Usage: receivesms.py -m smtp.server.com -e \"sms@server.com\" -f \"gsm@server.com\" -p 1234 -t 5 -g /dev/cuad0 -s 115200."
			print "       -m: SMTP server to use for sending the e-mail - REQUIRED"
			print "       -e: Email address to send to - REQUIRED"
			print "       -f: Email address to send from - REQUIRED"
			print "       -p: PIN number for SIM - optional (default: <BLANK>)"
			print "       -t: Minimum signal strength needed to send SMS in dBm - optional (default: 5)"
			print "       -g: COM port which the GSM modem is on - optional (default: /dev/cuad0)"
			print "       -s: COM port speed - optional (default: 115200)"
			
			exitProgram()
			
		else:
			for opt in opts:
				if opt[0] == "-e":
					email_to = opt[1]
					
				if opt[0] == "-f":
					email_from = opt[1]
					
				if opt[0] == "-g":
					gsm_port = opt[1]
					
				if opt[0] == "-m":
					email_gateway = opt[1]
					
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
	if email_to == "":
		print "Error: No e-mail address has been defined."
		exitProgram()
		
	if email_from == "":
		print "Error: No from e-mail address has been defined."
		exitProgram()
		
	if email_gateway == "":
		print "Error: No e-mail gateway has been defined."
		exitProgram()
		
	
	
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
							print "Information: Checking mailbox..."
							
							if gsm.sendATCommand("+CMGL=\"ALL\"", dualcheck = True):
								gsm.receiveLine()
								
								messages = []
								messages_to_delete = []
								
								while True:
									output = gsm.receiveLine()
									
									if output == "OK":
										break
										
									else:
										if output.startswith("+CMGL: "):
											header = output.replace("\"", "").split(": ")[1].split(",")
											message = gsm.receiveLine()
											
											if header[1].startswith("REC "):
												email_message = "Message ID %s has arrived from %s on %s at %s.\r\r\rMessage reads: -\r\r%s\r" % (header[0], header[2], header[4], header[5], message)
												
												# E-mail message
												try:
													print "Information: Sending e-mail for message ID %s..." % header[0]
													
													sendMail(email_gateway, email_from, email_to, "SMS Notification", email_message)
													
													# Once, we're happy add the message to the deletion list
													messages_to_delete.append(header[0])
													
												except Exception, e:
													print "Error: An error has occurred while sending the e-mail."
													print e
												
								
								print "Information: %d messages will be erased from SIM..." % len(messages_to_delete)
								
								for msg in messages_to_delete:
									
									if gsm.sendATCommand("+CMGD=%s" % msg, dualcheck = True):
										frc = gsm.receiveSingleResult()
										
										if frc == "OK":
											print "Information: Message ID %s has been erased from the SIM." % msg
											
										else:
											print "Warning: Message ID %s has NOT been erased from the SIM." % msg
										
									else:
										print "Error: +CMGD command not recognised, we don't have the commands needed to handle SMS."
							else:
								print "Error: +CMGL command not recognised, we don't have the commands needed to handle SMS."
								
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
	
def sendMail(smtp_server, from_address, to_address, subject, body):
	headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_address, to_address, subject)
	message = headers + body
	
	mailServer = smtplib.SMTP(smtp_server)
	mailServer.sendmail(from_address, to_address, message)
	mailServer.quit()
	

###############################
# Trigger the main subroutine #
###############################
if __name__ == "__main__":
	main()

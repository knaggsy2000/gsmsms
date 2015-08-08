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


from datetime import *
import getopt
from gsmdevice import GSMDevice
import os
import random
import sha
import smtplib
import sys
import time


gsm = None

gsm_bits = 8
gsm_parity = "N"
gsm_port = "/dev/cuad0"
gsm_speed = 115200
gsm_stop_bits = 1


# Constants
QUEUE_DIRECTORY = "queue"

VERSION = "0.2.1"


def audit(message):
	t = datetime.now()
	
	print "%s - %s" % (str(t.strftime("%d/%m/%Y %X")), message)
	
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
	
	server_mode = True
	
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
	print "Information: Welcome to SMS Server (GSMSMS v%s)." % VERSION
	print "Information: Please report any bugs you find so I can fix them!"
	print ""
	
	# Parse any arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ae:f:g:h:m:n:p:s:t:")
		
		if len(opts) == 0:
			print "Server usage: smsserver.py -m smtp.server.com -e \"sms@server.com\" -f \"gsm@server.com\" -p 1234 -t 5 -h 0 -g /dev/cuad0 -s 115200."
			print "          -m: SMTP server to use for sending the e-mail - REQUIRED"
			print "          -e: Email address to send to - REQUIRED"
			print "          -f: Email address to send from - REQUIRED"
			print "          -p: PIN number for SIM - optional (default: <BLANK>)"
			print "          -t: Minimum signal strength needed to send SMS in dBm - optional (default: 5)"
			print "          -h: Method to send SMS 0 = Send straight away, and 1 = Store message then send from storage - optional (default: 0)"
			print "          -g: COM port which the GSM modem is on - optional (default: /dev/cuad0)"
			print "          -s: COM port speed - optional (default: 115200)"
			print ""
			print "Queue usage:  smsserver.py -a -n \"+447912345678\" -m \"Hello\"."
			print "          -a: Indicates adding the message to the queue rather than running in server mode"
			print "          -n: Number in ISDN ITU E.164/E.163 format - REQUIRED"
			print "          -m: Message in double quotes - REQUIRED"
			
			exitProgram()
			
		else:
			for opt in opts:
				if opt[0] == "-a":
					server_mode = False
					
				if opt[0] == "-e":
					email_to = opt[1]
					
				if opt[0] == "-f":
					email_from = opt[1]
					
				if opt[0] == "-g":
					gsm_port = opt[1]
					
				if opt[0] == "-h":
					sms_method = int(opt[1])
					
				if opt[0] == "-m":
					if server_mode:
						email_gateway = opt[1]
						
					else:
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
	if not server_mode:
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
				
	else:
		if email_to == "":
			print "Error: No e-mail address has been defined."
			exitProgram()
			
		if email_from == "":
			print "Error: No from e-mail address has been defined."
			exitProgram()
			
		if email_gateway == "":
			print "Error: No e-mail gateway has been defined."
			exitProgram()
			
		
		if sms_method < 0 or sms_method > 1:
			print "Error: Unknown SMS sending method."
			exitProgram()
	
	
	# Setup any directories
	if not os.path.exists(QUEUE_DIRECTORY):
		os.mkdir(QUEUE_DIRECTORY)
	
	
	# OK, now determine what are doing
	if server_mode:
		# Setup the modem
		audit("Information: Connecting to GSM modem...")
		
		gsm = GSMDevice(gsm_port, gsm_speed, gsm_bits, gsm_parity, gsm_stop_bits, 1)
		
		# Connect to modem and ensure it's responding
		gsm.sendATCommand(skipcheck = True)
		frc = gsm.receiveSingleResult()
		
		if frc == "OK":
			# Modem is ready, re-setup...
			audit("Information: GSM modem responded.")
			
			if gsm.sendATCommand("E0", skipcheck = True):
				audit("Information: Checking if we need a PIN...")
				
				if gsm.sendATCommand("+CPIN?"):
					ir, frc = gsm.receiveDualResult()
					
					# Check if we need a PIN
					if ir == "+CPIN: SIM PIN":
						# PIN code needed, so send it
						audit("Information: PIN needed, sending...")
						
						gsm.sendATCommand("+CPIN=\"%s\"" % sim_pin, False)
						ir, frc = gsm.receiveDualResult()
						
						if frc == "OK":
							audit("Information: PIN accepted.")
							
						else:
							audit("Error: PIN not accepted.")
							
							exitProgram()
							
					elif ir == "+CPIN: SIM PUK":
						audit("Warning: SIM card is asking for PUK code.")
						
					elif ir == "+CPIN: SIM PUK2":
						audit("Warning: SIM card is asking for PUK2 code.")
						
					elif ir == "+CPIN: READY":
						audit("Information: No PIN required.")
						
					else:
						audit("Warning: Unexpected response '%s'." % frc)
						
					
					
					# Get the network we're on
					audit("Information: Determining network...")
					
					if gsm.sendATCommand("+COPS?", True):
						ir, frc = gsm.receiveDualResult()
						
						
						if frc == "OK":
							audit("Information: Network is %s." % ir.split(": ")[1].split(",")[2].replace("\"", ""))
							
						else:
							audit("Warning: Unable to get the network, command may not be supported.")
							
					else:
						audit("Warning: +COPS command not recognised, unable to get the network.")
						
					
					# Get the messaging centre number
					if gsm.sendATCommand("+CSCA?"):
						audit("Information: Checking for SMS messaging centre number...")
						
						ir, frc = gsm.receiveDualResult()
						
						if frc == "OK":
							audit("Information: Messaging centre is %s." % ir.split(": ")[1].split(",")[0].replace("\"", ""))
							
						else:
							audit("Warning: Unable to retreive the messaging centre number.")
							
					else:
						audit("Error: +CSCA command not recognised, unable to determine the messagin centre number.")
					
					
					
					# Make sure we have SMS commands available
					audit("Information: Determining SMS capabilities...")
					
					if gsm.sendATCommand("+CSMS?", dualcheck = True):
						audit("Information: Setting modem to TEXT mode...")
						
						if gsm.sendATCommand("+CMGF=1", dualcheck = True):
							frc = gsm.receiveSingleResult()
							
							if frc == "OK":
								# Once we're happy, enter the main loop
								audit("Information: Entering main loop...")
								
								while True:
									# Check for any messages to be sent
									audit("Information: Checking for messages to send...")
									
									for root, dirs, files in os.walk(QUEUE_DIRECTORY):
										for file in files:
											
											if file.endswith(".sms"):
												sms_to = ""
												sms_message = ""
												
												
												audit("Information: Processing \"%s\"..." % file)
												
												# Read the file, we only expect two lines
												try:
													f = open(os.path.join(QUEUE_DIRECTORY, file), "r")
													
													sms_to = f.readline().replace("\r" , "").replace("\n" , "")
													sms_message = f.readline().replace("\r" , "").replace("\n" , "")
													
												except Exception, e:
													audit("Error: Failed to read the SMS message from disk.")
													audit(e)
												
												
												if sms_to <> "" and sms_message <> "":
													# Get the signal strength, if it's too low we may not want to send it
													audit("Information: Determining signal strength...")
													
													if gsm.sendATCommand("+CSQ", dualcheck = True):
														ir, frc = gsm.receiveDualResult()
														
														
														if frc == "OK":
															csq = ir.split(": ")[1].split(",")
															dbm = int(csq[0])
															ber = int(csq[1])
															
															
															audit("Information: Signal strength is %ddBm with a BER of '%s'." % (dbm, gsm.getBERPercentage(ber).lower()))
															
															if dbm < minimum_signal_strength:
																audit("Warning: Signal strength is NOT acceptable (needed >= %ddBm), will try again later..." % minimum_signal_strength)
																
															else:
																if sms_to.startswith("+"):
																	sms_to_method = 0
																	
																	audit("Information: Number identified as ISDN ITU E.164/E.163.")
																	
																else:
																	sms_to_method = 1
																	
																	audit("Information: Number identified NOT as ISDN ITU E.164/E.163.")
																
																
																# Send the messages
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
																			audit("Information: SMS has been sent - %s." % ir)
																			
																			audit("Information: Removing file from queue...")
																			os.unlink(os.path.join(QUEUE_DIRECTORY, file))
																			
																		else:
																			audit("Error: SMS has failed to be sent.")
																			
																		gsm.changeTimeout(1)
																		
																	else:
																		audit("Error: +CMGS command not recognised, we don't have the commands needed to handle SMS.")
																	
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
																			
																			audit("Information: Message stored in memory index %d." % index)
																			audit("Information: Sending SMS from storage...")
																			
																			gsm.changeTimeout(30)
																			
																			if gsm.sendATCommand("+CMSS=%d" % index):
																				ir, frc = gsm.receiveDualResult()
																				
																				if frc == "OK":
																					audit("Information: SMS has been sent - %s." % ir)
																					
																					audit("Information: Removing file from queue...")
																					os.unlink(file)
																					
																					
																					audit("Information: Erasing message from storage...")
																					
																					gsm.changeTimeout(1)
																					
																					if gsm.sendATCommand("+CMGD=%d" % index, dualcheck = True):
																						frc = gsm.receiveSingleResult()
																						
																						if frc == "OK":
																							audit("Information: Erase successful.")
																							
																						else:
																							audit("Warning: Erase was NOT successful.")
																						
																					else:
																						audit("Warning: +CMGD command not recognised, we don't have the commands needed to erase message from memory.")
																					
																				else:
																					audit("Error: SMS has failed to be sent.")
																					
																			else:
																				audit("Error: The message has failed to get saved into memory.")
																			
																			gsm.changeTimeout(1)
																			
																		else:
																			audit("Error: The message has failed to get saved into memory.")
																			
																	else:
																		audit("Error: +CMGW command not recognised, we don't have the commands needed to handle SMS.")
															
														else:
															audit("Warning: Unable to get the signal strength, command may not be supported.")
															
													else:
														audit("Warning: +CSQ command not recognised, unable to get the signal strength.")
												else:
													audit("Warning: Unable to correctly read in the file, cannot send.")
												
											else:
												audit("Warning: Unknown file \"%s\" in queue directory, skipping...")
										
										
										
									
									
									# Check for any message that need to be received
									audit("Information: Checking for messages to receive...")
									
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
															audit("Information: Sending e-mail for message ID %s..." % header[0])
															
															sendMail(email_gateway, email_from, email_to, "SMS Notification", email_message)
															
															# Once, we're happy add the message to the deletion list
															messages_to_delete.append(header[0])
															
														except Exception, e:
															audit("Error: An error has occurred while sending the e-mail.")
															audit(e)
														
										
										if len(messages_to_delete) > 0:
											audit("Information: %d messages will be erased from SIM..." % len(messages_to_delete))
											
											for msg in messages_to_delete:
												
												if gsm.sendATCommand("+CMGD=%s" % msg, dualcheck = True):
													frc = gsm.receiveSingleResult()
													
													if frc == "OK":
														audit("Information: Message ID %s has been erased from the SIM." % msg)
														
													else:
														audit("Warning: Message ID %s has NOT been erased from the SIM." % msg)
													
												else:
													audit("Error: +CMGD command not recognised, we don't have the commands needed to handle SMS.")
									else:
										audit("Error: +CMGL command not recognised, we don't have the commands needed to handle SMS.")
									
									
									# Wait...
									audit("Information: Sleeping...")
									
									time.sleep(60)
									#time.sleep(time.localtime(time.time())[5])
						else:
							print "Error: Unable to enter TEXT mode."
							exitProgram()
							
					else:
						print "Error: +CSMS command not recognised, we don't have the commands needed to handle SMS."
						exitProgram()
						
				else:
					print "Error: +CPIN command not recognised, please ensure we're talking to a GSM modem."
					exitProgram()
					
			else:
				print "Error: E0 command not recognised, please ensure we're talking to a GSM modem."
				exitProgram()
			
		else:
			print "Error: The modem doesn't appear to be ready.  Please ensure you have selected the correct COM port and settings."
			exitProgram()
		
	else:
		print "Information: Adding message to queue..."
		
		try:
			new_file = uuid()
			
			f = open(os.path.join(QUEUE_DIRECTORY, "%s.sms" % new_file), "w")
			f.write("%s\n%s\n" % (sms_to, sms_message))
			f.close()
			
			print "Information: \"%s.sms\" has been added into the queue." % new_file
			
		except Exception, e:
			print "Error: Failed to create the SMS file to add to the queue, please check directory permissions."
			print e
		
		
		print "Information: Exiting..."
		exitProgram()
	
def sendMail(smtp_server, from_address, to_address, subject, body):
	headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (from_address, to_address, subject)
	message = headers + body
	
	mailServer = smtplib.SMTP(smtp_server)
	mailServer.sendmail(from_address, to_address, message)
	mailServer.quit()
	
def uuid(*args):
	t = long(time.time() * 1000)
	r = long(random.random() * 100000000000000000L)
	a = None
	
	try:
		a = socket.gethostbyname(socket.gethostname())
	
	except:
		# We can't get a network address, so improvise
		a = random.random() * 100000000000000000L
	
	data = str(t) + " " + str(r) + " " + str(a) + str(args)
	
	return sha.sha(data).hexdigest()
	

###############################
# Trigger the main subroutine #
###############################
if __name__ == "__main__":
	main()

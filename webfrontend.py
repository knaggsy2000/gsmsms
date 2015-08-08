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


import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import getopt
import os
import random
import sha
import string
import sys
import time


QUEUE_DIRECTORY = "queue"

VERSION = "0.2.1"


class HTTPHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			request = os.path.join(self.path.replace("/", ""))
			
			if request.endswith(".html"):
				f = open(request)
				
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write(f.read())
				
				f.close()
				
			elif request == "":
				f = open("sendsms.html")
				
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write(f.read())
				
				f.close()
				
			else:
				self.send_error(403, "Forbidden")
			
		except IOError:
			self.send_error(404, "File Not Found: %s" % self.path)
			
		except:
			self.send_error(400, "Bad request")
	
	def do_POST(self):
		global rootnode
		
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader("content-type"))
			
			if ctype == "multipart/form-data":
				query = cgi.parse_multipart(self.rfile, pdict)
				
			self.send_response(301)
			self.end_headers()
			
			sms_to = query.get("mobilenumber")[0]
			sms_message = query.get("message")[0]
			
			if sms_to <> "" and sms_message <> "":
				if len(sms_message) > 140:
					self.wfile.write("<html>Error: Message must be less than or equal to 140 characters</html>")
					
				else:
					try:
						new_file = uuid()
						
						f = open(os.path.join(QUEUE_DIRECTORY, "%s.sms" % new_file), "w")
						f.write("%s\n%s\n" % (sms_to, sms_message))
						f.close()
						
						self.wfile.write("<html>Information: \"%s.sms\" has been added into the queue.</html>" % new_file)
						
					except Exception, e:
						self.wfile.write("<html>Error: Failed to create the SMS file to add to the queue.<br><br>%s</html>" % e)
					
			else:
				self.wfile.write("<html>Error: You must fill in both fields.</html>")
			
		except Exception, e:
			print "Error: An error has occurred while processing the POST."
			print e
	
def exitProgram():
	sys.exit()
	
def main():
	server = None
	server_address = ""
	server_port = 12345
	
	
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
	print "Information: Welcome to the Web Frontend for the SMS Server (GSMSMS v%s)." % VERSION
	print "Information: Please report any bugs you find so I can fix them!"
	print ""
	
	
	# Parse the arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "a:p:")
		
		if len(opts) == 0:
			print "Server usage: webfrontend.py -a \"localhost\" -p 12345."
			print "          -a: Address to listen on (can be blank e.g. \"\") - REQUIRED"
			print "          -p: Port to listen on - REQUIRED"
			
			exitProgram()
			
		else:
			for opt in opts:
				if opt[0] == "-a":
					server_address = opt[1]
					
				if opt[0] == "-p":
					server_port = int(opt[1])
					
	except Exception, e:
		print "Error: An error has occurred while processing the arguments."
		print e
		
		exitProgram()
	
	
	# Now fire up the web service
	try:
		server = HTTPServer((server_address, server_port), HTTPHandler)
		
		print "Information: Starting webserver on port %d..." % server_port
		server.serve_forever()
		
	except Exception, e:
		print "Information: Shutting down..."
		
		try:
			server.socket.close()
			
		except:
			pass
		
		print "Error: An error has occurred while serving web requests."
		print e
	
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

# Kagura RPC plugin for sublime text 3.
#
# Refer to these if you never worked on subl plugins before: 
#  http://www.sublimetext.com/docs/plugin-basics
#  http://www.sublimetext.com/docs/plugin-examples
#  http://www.sublimetext.com/docs/api-reference
# <ctrl> + ~ to see console output for debugging!
import sublime, sublime_plugin
import re
import http.client
import sys
import socket
import subprocess


def KaguraHost():
	return "localhost"


def KaguraPort():
	return 8080


def KaguraGetLanIp():
	# Trick to get lan IP from localhost. Can't remember were I first saw this.
	s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	s.connect( ( "google.com", 80 ) )
	host = s.getsockname()[0]
	s.close()
	return host


def KaguraIsScript( filename ):
	ext = re.compile(".*\.(lua|script)$")
	return ext.match( filename ) is not None


def KaguraIsShader( filename ):
	ext = re.compile(".*\.(shader)$")
	return ext.match( filename ) is not None


def KaguraRpcHttp( url, host = KaguraHost(), port = KaguraPort() ):
	msg = host + ":" + str( port ) + url
	sublime.status_message( msg )
	print( msg )
	response = None

	try:
		conn = http.client.HTTPConnection( host, port, timeout=5 )
		conn.request( "GET", url )
		reply = conn.getresponse()
		response = reply.read()
		conn.close()

		sublime.status_message( str( reply.status ) + " " + " " + reply.reason )
		# logging.log( 41, response )
		print( response )

	except:
		sublime.error_message( "Connection refused:\n" + msg )

	return response


class KaguraReloadScriptCommand( sublime_plugin.TextCommand ):
	def run( self, edit):
		filename = self.view.file_name()

		if KaguraIsScript( filename ) :
			print( "Rpc server at " + host + ":" + str( port ) )
			
			# Default is to reload (current view) script file.
			# Needs to be relative path!
			splits = filename.rsplit( "scripts/", 1 )
			if splits :
				filename = "scripts/" + splits[1]

			KaguraRpcHttp( "/kaScript?KaReloadScript('" + filename + "')" )


class KaguraReloadShaderCommand( sublime_plugin.TextCommand ):
	def run( self, edit):
		filename = self.view.file_name()

		if KaguraIsShader( filename ) :			
			# Default is to reload (current view) script file.
			# Needs to be relative path!
			splits = filename.rsplit( "shaders/", 1 )
			if splits :
				filename = splits[1]

			splitsB = filename.rsplit( ".shader", 1 )
			if splitsB :
				filename = splitsB[0]

			KaguraRpcHttp( "/kaScript?KaShaderReload('" + filename + "')" )


class KaguraRpcCommand( sublime_plugin.ApplicationCommand ):
	def run( self, args ):
		KaguraRpcHttp( "/kaScript?" + args )


class KaguraLanIpCommand( sublime_plugin.ApplicationCommand ):
	def run( self, args ):
		sublime.message_dialog( KaguraGetLanIp() )


class KaguraShellCommand( sublime_plugin.ApplicationCommand ):
	def run( self, args ):
		# Hack to get project path without using os module, as it is broken for some subl.
		wdir = sublime.active_window().project_file_name().rsplit( '/', 1 )[0]
		sublime.status_message( "Running " + args + " ..." )
		ret = subprocess.call( args + " &", 
			shell=True,
			cwd=wdir )

		if ret :
			sublime.status_message( args + " : " + str( ret ) )


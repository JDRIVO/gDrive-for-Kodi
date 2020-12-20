'''
	gdrive (Google Drive ) for KODI / XBMC Plugin
	Copyright (C) 2013-2016 ddurdle

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

# cloudservice - required python modules
import os
import re
import sys
import urllib, urllib2
import socket
import cookielib

# cloudservice - standard modules
from cloudservice import cloudservice
from resources.lib import authorization

# cloudservice - standard XBMC modules
import xbmc, xbmcgui

SERVICE_NAME = 'dmdgdrive'

#
# Google Drive API 2 implementation of Google Drive
#
class gdrive(cloudservice):
	API_VERSION = '3.0'
	PROTOCOL = 'https://'
	API_URL = PROTOCOL + 'www.googleapis.com/drive/v2/'

	##
	# initialize (save addon, instance name, user agent)
	##
	def __init__(self, plugin_handle, PLUGIN_URL, addon, instanceName, user_agent, settings, authenticate=True):
		self.plugin_handle = plugin_handle
		self.PLUGIN_URL = PLUGIN_URL
		self.addon = addon
		self.instanceName = instanceName
		self.settings = settings
		self.failed = False

		try:
			username = self.getInstanceSetting('username')
			#username = self.getInstanceSetting(str(instanceName) + '_username')
		except:
			username = ''

		self.authorization = authorization.authorization(username)
		self.cookiejar = cookielib.CookieJar()
		self.user_agent = user_agent

		# load the OAUTH2 tokens or force fetch if not set
		if (authenticate == True and (not self.authorization.loadToken(self.instanceName, addon, 'auth_access_token') or not self.authorization.loadToken(self.instanceName, addon, 'auth_refresh_token') ) ):

			if self.getInstanceSetting('code'):
				self.getToken(self.getInstanceSetting('code') )
			else:
				xbmcgui.Dialog().ok(self.addon.getLocalizedString(30003), self.addon.getLocalizedString(30005) )
				self.failed = True
				return

	##
	# get OAUTH2 access and refresh token for provided code
	#	parameters: OAUTH2 code
	#	returns: none
	##
	def getToken(self, code):
		url = 'https://accounts.google.com/o/oauth2/token'
		clientID = self.getInstanceSetting('client_id')
		clientSecret = self.getInstanceSetting('client_secret')
		header = {'User-Agent' : self.user_agent, 'Content-Type' : 'application/x-www-form-urlencoded'}
		req = urllib2.Request(url, 'code=' + str(code) + '&client_id=' + str(clientID + '&client_secret=' + str(clientSecret) + '&redirect_uri=urn:ietf:wg:oauth:2.0:oob&grant_type=authorization_code', header) )

		# try login
		try:
			response = urllib2.urlopen(req)
		except urllib2.URLError, e:
			xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30017) )
			xbmc.log(str(e) )
			return

		response_data = response.read()
		response.close()

		# retrieve authorization token
		for r in re.finditer('\"access_token\"\s?\:\s?\"([^\"]+)\".+?' + '\"refresh_token\"\s?\:\s?\"([^\"]+)\".+?', response_data, re.DOTALL):
			accessToken, refreshToken = r.groups()
			self.authorization.setToken('auth_access_token', accessToken)
			self.authorization.setToken('auth_refresh_token', refreshToken)
			self.updateAuthorization(self.addon)
			xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30142) )

		for r in re.finditer('\"error_description\"\s?\:\s?\"([^\"]+)\"', response_data, re.DOTALL):
			errorMessage = r.group(1)
			xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30119) + errorMessage)
			xbmc.log(errorMessage)

		return

	##
	# refresh OAUTH2 access given refresh token
	#	parameters: none
	#	returns: none
	##
	def refreshToken(self):
		url = 'https://accounts.google.com/o/oauth2/token'
		clientID = self.getInstanceSetting('client_id')
		clientSecret = self.getInstanceSetting('client_secret')
		header = {'User-Agent' : self.user_agent, 'Content-Type': 'application/x-www-form-urlencoded'}
		req = urllib2.Request(url, 'client_id=' + clientID + '&client_secret=' + clientSecret + '&refresh_token=' + self.authorization.getToken('auth_refresh_token') + '&grant_type=refresh_token', header)

		# try login
		try:
			response = urllib2.urlopen(req)
		except urllib2.URLError, e:
			xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30017) )
			xbmc.log(str(e) )
			return

		response_data = response.read()
		response.close()

		# retrieve authorization token
		for r in re.finditer('\"access_token\"\s?\:\s?\"([^\"]+)\".+?', response_data, re.DOTALL):
			accessToken = r.group(1)
			self.authorization.setToken('auth_access_token', accessToken)
			self.updateAuthorization(self.addon)

		for r in re.finditer('\"error_description\"\s?\:\s?\"([^\"]+)\"', response_data, re.DOTALL):
			errorMessage = r.group(1)
			xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30119) + errorMessage)
			xbmc.log(errorMessage)

		return

	##
	# return the appropriate "headers" for Google Drive requests that include 1) user agent, 2) authorization token
	#	returns: list containing the header
	##
	def getHeadersList(self, isPOST=False, additionalHeader=None, additionalValue=None, isJSON=False):

		if self.authorization.isToken(self.instanceName, self.addon, 'auth_access_token') and not isPOST:
#			 return { 'User-Agent' : self.user_agent, 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
			if additionalHeader is not None:
				return {'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token'), additionalHeader : additionalValue}
			else:
				return {'Cookie' : 'DRIVE_STREAM='+ self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token')}

		elif isJSON and self.authorization.isToken(self.instanceName,self.addon, 'auth_access_token'):
#			 return { 'User-Agent' : self.user_agent, 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
			return {'Content-Type': 'application/json', 'Cookie' : 'DRIVE_STREAM=' + self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token')}

		elif self.authorization.isToken(self.instanceName, self.addon, 'auth_access_token'):
#			 return { 'User-Agent' : self.user_agent, 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }
			return {"If-Match" : '*', 'Content-Type': 'application/atom+xml', 'Cookie' : 'DRIVE_STREAM=' + self.authorization.getToken('DRIVE_STREAM'), 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token')}
			#return {  'Content-Type': 'application/atom+xml', 'Authorization' : 'Bearer ' + self.authorization.getToken('auth_access_token') }

		elif self.authorization.isToken(self.instanceName,self.addon, 'DRIVE_STREAM') and not isPOST:

			if additionalHeader is not None:
				return {'Cookie' : 'DRIVE_STREAM=' + self.authorization.getToken('DRIVE_STREAM'), additionalHeader : additionalValue}
			else:
				return {'Cookie' : 'DRIVE_STREAM=' + self.authorization.getToken('DRIVE_STREAM')}

		else:
			return {'User-Agent' : self.user_agent}

	##
	# return the appropriate "headers" for Google Drive requests that include 1) user agent, 2) authorization token, 3) api version
	#	returns: URL-encoded header string
	##
	def getHeadersEncoded(self):

		return urllib.urlencode(self.getHeadersList() )
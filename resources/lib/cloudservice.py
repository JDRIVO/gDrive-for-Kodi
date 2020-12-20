'''
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

import re
import urllib
import sys
import os

PLUGIN_URL = sys.argv[0]

def decode(data):

	return re.sub("&#(\d+)(;|(?=\s))", _callback, data).strip()

def decode_dict(data):

	for k, v in data.items():

		if type(v) is str or type(v) is unicode:
			data[k] = decode(v)

	return data

#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
	id = matches.group(1)

	try:
		return unichr(int(id) )
	except:
		return id

#
#
#
class cloudservice(object):
	# CloudService v0.2.3

	PLAYBACK_RESOLVED = 1
	PLAYBACK_PLAYER = 2
	PLAYBACK_NONE = 3

	def __init__(self): pass

	def getInstanceSetting(self, setting, default=None):

		try:
			return self.addon.getSetting(self.instanceName + '_' + setting)
		except:
			return default

	##
	# perform login
	##
	def login(self): pass

	##
	# if we don't have an authorization token set for the plugin, set it with the recent login.
	#	auth_token will permit "quicker" login in future executions by reusing the existing login session (less HTTPS calls = quicker video transitions between clips)
	##
	def updateAuthorization(self, addon):

		if self.authorization.isUpdated: #and addon.getSetting(self.instanceName+'_save_auth_token') == 'true':
			self.authorization.saveTokens(self.instanceName, addon)

	##
	# return the appropriate "headers" for requests that include 1) user agent, 2) any authorization cookies/tokens
	#	returns: list containing the header
	##
	def getHeadersList(self, isPOST=False, additionalHeader=None, additionalValue=None, isJSON=False):

		return {'User-Agent' : self.user_agent}

	##
	# return the appropriate "headers" for requests that include 1) user agent, 2) any authorization cookies/tokens
	#	returns: URL-encoded header string
	##
	def getHeadersEncoded(self):

		return urllib.urlencode(self.getHeadersList() )
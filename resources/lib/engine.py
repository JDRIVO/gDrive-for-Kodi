'''
    CloudService XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

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
import sys
import os
import urllib, urllib2
import xbmc, xbmcgui, xbmcplugin, xbmcvfs

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

class contentengine(object):
	plugin_handle = None
	PLUGIN_URL = ''

	##
	# load eclipse debugger
	#	parameters: none
	##
	def debugger(self):

		try:
			remote_debugger = settingsModule.getSetting('remote_debugger')
			remote_debugger_host = settingsModule.getSetting('remote_debugger_host')

			# append pydev remote debugger
			if remote_debugger == 'true':
				# Make pydev debugger works for auto reload.
				# Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
				import pysrc.pydevd as pydevd
				# stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
				pydevd.settrace(remote_debugger_host, stdoutToServer=True, stderrToServer=True)

		except ImportError:
			xbmc.log(self.addon.getLocalizedString(30016), xbmc.LOGERROR)
			sys.exit(1)
		except:
			return

	##
	# add a menu to a directory screen
	#	parameters: url to resolve, title to display, optional: icon, fanart, total_items, instance name
	##
	def addMenu(self, url, title, total_items=0, instanceName=None):
		listitem = xbmcgui.ListItem(title)

		if instanceName is not None:
			cm = []
			cm.append( (self.addon.getLocalizedString(30219), 'RunPlugin(' + self.PLUGIN_URL + '?mode=makedefault&instance=' + instanceName + ')' ) )
			cm.append( (self.addon.getLocalizedString(30159), 'RunPlugin(' + self.PLUGIN_URL + '?mode=delete&instance=' + instanceName + ')' ) )
			listitem.addContextMenuItems(cm, True)

		xbmcplugin.addDirectoryItem(self.plugin_handle, url, listitem, isFolder=True, totalItems=total_items)

	##
	# Calculate the number of accounts defined in settings
	#	parameters: the account type (usually plugin name)
	##
	def numberOfAccounts(self, accountType):

		return 9

	##
	# Delete an account, enroll an account or refresh the current listings
	#	parameters: mode
	##
	def accountActions(self, addon, mode, instanceName, numberOfAccounts):

		if mode == 'dummy':
			xbmc.executebuiltin("Container.Refresh")

		elif mode == 'makedefault':
			addon.setSetting('account_default', instanceName[-1])

		# delete the configuration for the specified account
		elif mode == 'delete':

			if instanceName != '':

				try:
					# gdrive specific ***
					addon.setSetting(instanceName + '_username', '')
					addon.setSetting(instanceName + '_code', '')
					addon.setSetting(instanceName + '_client_id', '')
					addon.setSetting(instanceName + '_client_secret', '')

					xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30158) )
				except:
					#error: instance doesn't exist
					xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30158) )

			xbmc.executebuiltin("Container.Refresh")

		# enroll a new account
		elif mode == 'enroll':

			import socket
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.connect( ("8.8.8.8", 80) )
			IP = s.getsockname()[0]
			s.close()

			xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30210) + ' http://' + str(IP) + ':8011/enroll' + ' ' + addon.getLocalizedString(30218) )
			mode = 'main'

	##
	# Delete an account, enroll an account or refresh the current listings
	#	parameters: addon, plugin name, mode, instance name, user provided username, number of accounts, current context
	#	returns: selected instance name
	##
	def getInstanceName(self, addon, mode, instanceName, invokedUsername, numberOfAccounts, contextType, settingsModule):

		# show list of services
		if mode == 'delete' or mode == 'makedefault' or mode == 'dummy':
			count = 1

		elif numberOfAccounts > 1 and instanceName == '' and invokedUsername == '' and mode == 'main':
			self.addMenu(self.PLUGIN_URL + '?mode=enroll&content_type=' + str(contextType), '[' + str(addon.getLocalizedString(30207) ) + ']')
			mode = ''
			count = 1

			while True:
				instanceName = self.PLUGIN_NAME + str(count)
				username = settingsModule.getSetting(instanceName + '_username', None)
				type = settingsModule.getSetting(instanceName + '_type', None)

				if username is not None and username != '':
					self.addMenu(self.PLUGIN_URL + '?mode=main&content_type=' + str(contextType) + '&instance=' + str(instanceName), username, instanceName=instanceName)

				if (username is None or username == '') and (type is None or type == ''):
					break

				count = count + 1

			return None

		elif instanceName == '' and invokedUsername == '' and numberOfAccounts == 1:
			count = 1
			options = []
			accounts = []

			for count in range (1, numberOfAccounts + 1):
				instanceName = self.PLUGIN_NAME + str(count)

				try:
					username = settingsModule.getSetting(instanceName + '_username')

					if username != '' and username is not None:
						options.append(username)
						accounts.append(instanceName)

					if username != '' and username is not None:
						return instanceName

				except:
					return instanceName

			#fallback on first defined account
			return accounts[0]

		# no accounts defined
		elif numberOfAccounts == 0:
			xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30015) )
			xbmcplugin.endOfDirectory(self.plugin_handle)

			return instanceName

		# show entries of a single account (such as folder)
		elif instanceName != '':
			return instanceName

		elif invokedUsername != '':
			options = []
			accounts = []

			for count in range (1, numberOfAccounts + 1):
				instanceName = self.PLUGIN_NAME + str(count)

				try:
					username = settingsModule.getSetting(instanceName + '_username')

					if username != '' and username is not None:
						options.append(username)
						accounts.append(instanceName)

					if username == invokedUsername:
						return instanceName

				except:
					return instanceName

			#fallback on first defined account
			return accounts[0]

		#prompt before playback
		else:
			options = []
			accounts = []

			for count in range (1, numberOfAccounts + 1):
				instanceName = self.PLUGIN_NAME + str(count)

				try:
					username = settingsModule.getSetting(instanceName + '_username', 10)

					if username != '' and username is not None:
						options.append(username)
						accounts.append(instanceName)

				except:
					break

			ret = xbmcgui.Dialog().select(addon.getLocalizedString(30120), options)

			#fallback on first defined account
			if accounts[ret] == 'public':
				return None
			else:
				return accounts[ret]

	def run(self, dbID=None, dbType=None, writer=None, query=None, DBM=None, addon=None, host=None):
		from resources.lib import settings
		import constants

		addon = constants.addon
		self.addon = addon
		self.PLUGIN_URL = constants.PLUGIN_NAME
		self.PLUGIN_NAME = constants.PLUGIN_NAME

		cloudservice2 = constants.cloudservice2

		#global variables
		self.PLUGIN_URL = sys.argv[0]
		self.plugin_handle = int(sys.argv[1])
		plugin_queries = settings.parse_query(sys.argv[2][1:])

		# cloudservice - create settings module
		settingsModule = settings.settings(addon)

		# retrieve settings
		user_agent = settingsModule.getSetting('user_agent')
		#obsolete, replace, revents audio from streaming
		#if user_agent == 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)':
		#	 addon.setSetting('user_agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.38 Safari/532.0')

		mode = settingsModule.getParameter('mode', 'main')

		# make mode case-insensitive
		mode = mode.lower()

		try:
			instanceName = (plugin_queries['instance']).lower()
		except:
			instanceName = ''

		# cloudservice - content type
		contextType = settingsModule.getParameter('content_type')

		xbmcplugin.addSortMethod(self.plugin_handle, xbmcplugin.SORT_METHOD_LABEL)
		xbmcplugin.addSortMethod(self.plugin_handle, xbmcplugin.SORT_METHOD_SIZE)

		numberOfAccounts = self.numberOfAccounts(constants.PLUGIN_NAME)
		invokedUsername = settingsModule.getParameter('username')

		# cloudservice - utilities
		###
		if mode == 'dummy' or mode == 'delete' or mode == 'makedefault' or mode == 'enroll':
			self.accountActions(addon, mode, instanceName, numberOfAccounts)
			settings = settingsModule.__init__(addon)
			mode = 'main'
			instanceName = ''

		#STRM playback without instance name; use default
		if invokedUsername == '' and instanceName == '' and mode == 'video':
			instanceName = constants.PLUGIN_NAME + str(settingsModule.getSetting('account_default', 1) )

		instanceName = self.getInstanceName(addon, mode, instanceName, invokedUsername, numberOfAccounts, contextType, settingsModule)

		service = None

		if instanceName is None and (mode == 'index' or mode == 'main'):
			service = None
		elif instanceName is None or instanceName == '':
			service = cloudservice2(self.plugin_handle, self.PLUGIN_URL, addon, '', user_agent, settingsModule, authenticate=False, DBM=DBM)
		else:
			service = cloudservice2(self.plugin_handle, self.PLUGIN_URL, addon, instanceName, user_agent, settingsModule, DBM=DBM)

		if service is None:
			xbmcplugin.endOfDirectory(self.plugin_handle)
			return

		###
		# for video files - playback of video
		# force stream - play a video given its url
		###
		elif mode == 'video':
			filename = settingsModule.getParameter('filename') #file ID

			try:
				service
			except NameError:
				xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30051) + addon.getLocalizedString(30052) )
				xbmc.log(addon.getLocalizedString(30051) + constants.PLUGIN_NAME + '-login', xbmc.LOGERROR)
				xbmcplugin.endOfDirectory(self.plugin_handle)
				return

			if settingsModule.cryptoPassword != "":

				if dbType == 'movie':
					jsonQuery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": "1", "method": "VideoLibrary.GetMovieDetails", "params": { "movieid":' + str(dbID) + ', "properties": ["resume"] } }')
					jsonKey = 'moviedetails'
				else:
					jsonQuery = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": "1", "method": "VideoLibrary.GetEpisodeDetails", "params": { "episodeid":' + str(dbID) + ', "properties": ["resume"] } }')
					jsonKey = 'episodedetails'

				import json
				jsonQuery = jsonQuery.encode('utf-8', errors='ignore')
				jsonResponse = json.loads(jsonQuery)
				resumeData = jsonResponse['result'][jsonKey]['resume']

				resumePosition = resumeData['position']
				videoLength = resumeData['total']

				resumeOption = False

				# import pickle

				# resumeDBPath = xbmcvfs.translatePath(settingsModule.resumeDBPath)
				# resumeDB = os.path.join(resumeDBPath, 'kodi_resumeDB.p')

				# try:
					# with open(resumeDB, 'rb') as dic:
						# videoData = pickle.load(dic)
				# except:
					# videoData = {}

				# try:
					# resumePosition = videoData[filename]
				# except:
					# videoData[filename] = 0
					# resumePosition = 0

				# VideoDB = xbmcvfs.translatePath(settingsModule.resumeDBPath)
				# #dbPath = os.path.join(xbmc.translatePath("special://database"), 'MyVideos119.db')
				# db = sqlite.connect(VideoDB)

				# strmName = settingsModule.getParameter('title') + ".strm"
				# cursor = list(db.execute('SELECT timeInSeconds FROM bookmark WHERE idFile=(SELECT idFile FROM files WHERE strFilename="%s")' % strmName) )

				# if cursor:
					# resumePosition = cursor[0][0]
				# else:
					# resumePosition = 0

				if resumePosition > 0:

					import time
					options = []
					options.append('Resume from ' + str(time.strftime("%H:%M:%S", time.gmtime(resumePosition) ) ) )
					options.append('Play from beginning')

					selection = xbmcgui.Dialog().contextmenu(options)

					if selection == 0:
						# resumePosition = resumePosition / total * 100
						resumeOption = True
					#elif selection == 1:
						# resumePosition = '0'
						#videoData[filename] = 0
					elif selection == -1:
						return

				driveURL = "https://www.googleapis.com/drive/v2/files/%s?includeTeamDriveItems=true&supportsTeamDrives=true&alt=media" % filename
				url = 'http://localhost:' + str(service.settings.streamPort) + '/crypto_playurl'
				req = urllib2.Request(url, 'instance=' + str(service.instanceName) + '&url=' + driveURL)

				try:
					response = urllib2.urlopen(req)
					response.close()
				except urllib2.URLError, e:
					xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)

				item = xbmcgui.ListItem(path='http://localhost:' + str(service.settings.streamPort) + '/play')
				#item.setProperty('StartPercent', str(position) )
				#item.setProperty('startoffset', '60')

				if resumeOption:
					#item.setProperty('totaltime', '1')
					item.setProperty('totaltime', str(videoLength) )
					item.setProperty('resumetime', str(resumePosition) )

				xbmcplugin.setResolvedUrl(self.plugin_handle, True, item)
				from resources.lib import gPlayer
				player = gPlayer.gPlayer(dbID=dbID, dbType=dbType)

				#with open(resumeDB, 'w+') as dic:
				#	pickle.dump(videoData, dic)

				#del videoData

				xbmc.sleep(100)
				monitor = xbmc.Monitor()

				while not monitor.abortRequested() and not player.isExit:
					player.sleep()
					player.saveTime()

				#with open(resumeDB, 'r') as dic:
				#	videoData = pickle.load(dic)

				#if player.videoWatched:
				#	del videoData[filename]
				#else:
				#	videoData[filename] = player.time

				#with open(resumeDB, 'w+') as dic:
				#	pickle.dump(videoData, dic)

				# if dbType == 'movie':
					# xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.RefreshMovie", "params": {"movieid":' + str(dbID) + ', "ignorenfo": true}, "id": "1"}')
				# elif dbType == 'episode':
					# xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.RefreshEpisode", "params": {"episodeid":' + str(dbID) + ', "ignorenfo": true}, "id": "1"}')

				#request = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, "limits": { "start" : 0 }, "properties": ["playcount"], "sort": { "order": "ascending", "method": "label" } }, "id": "libMovies"}
				#request = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, "limits": { "start" : 0 }, "properties": ["playcount"], "sort": { "order": "ascending", "method": "label" } }, "id": "libMovies"}

		xbmcplugin.endOfDirectory(self.plugin_handle)
		return

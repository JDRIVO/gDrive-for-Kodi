import time
import xbmc
from resources.lib import settings
import constants

addon = constants.addon
settingsModule = settings.settings(addon)

class gPlayer(xbmc.Player):

	def __init__(self, *args, **kwargs):
		xbmc.Player.__init__(self)
		self.dbID = kwargs["dbID"]
		self.dbType = kwargs["dbType"]
		self.movieWatchTime = settingsModule.movieWatchTime
		self.tvWatchTime = settingsModule.tvWatchTime
		self.isExit = False
		self.videoDuration = None

		if self.dbType == "movie":
			self.isMovie = True
			self.markedWatched = self.movieWatchTime
		else:
			self.isMovie = False
			self.markedWatched = self.tvWatchTime

	def onPlayBackStarted(self):

		while not self.videoDuration:

			try:
				self.videoDuration = self.getTotalTime()
			except:
				self.isExit = True
				return

			xbmc.sleep(100)

	def onPlayBackStopped(self):

		try:
			videoProgress = self.time / self.videoDuration * 100

			if videoProgress < float(self.markedWatched):

				if self.isMovie:

					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "resume": {"position": %d, "total": %d } } }' % (self.dbID, self.time, self.videoDuration ) )
				else:

					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "resume": {"position": %d, "total": %d } } }' % (self.dbID, self.time, self.videoDuration) )
			else:

				if self.isMovie:
					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount": 1 , "resume": {"position": 0} } }' % self.dbID)

				else:
					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount": 1 , "resume": {"position": 0} } }' % self.dbID)

				xbmc.executebuiltin("ReloadSkin")

			self.isExit = True
		except:
			self.isExit = True

	def onPlayBackEnded(self):

		try:
			videoProgress = self.time / self.videoDuration * 100

			if videoProgress < float(self.markedWatched):

				if self.isMovie:

					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "resume": {"position": %d, "total": %d } } }' % (self.dbID, self.time, self.videoDuration ) )
				else:

					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "resume": {"position": %d, "total": %d } } }' % (self.dbID, self.time, self.videoDuration) )
			else:

				if self.isMovie:
					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount": 1 , "resume": {"position": 0} } }' % self.dbID)

				else:
					timeEnd = time.time() + 1

					while time.time() < timeEnd:
						xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount": 1 , "resume": {"position": 0} } }' % self.dbID)

				xbmc.executebuiltin("ReloadSkin")

			self.isExit = True
		except:
			self.isExit = True

	def onPlayBackPaused(self):
		self.saveTime()

	def onPlayBackResumed(self):
		self.saveTime()

	def onPlayBackSeekChapter(self):
		self.saveTime()

	def onPlayBackSeek(self, time, seekOffset):
		self.saveTime()

	def saveTime(self):

		try:
			self.time = self.getTime()
		except:
			self.onPlayBackStopped()

	def sleep(self):
		xbmc.sleep(100)

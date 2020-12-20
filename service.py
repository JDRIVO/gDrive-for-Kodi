import threading
import xbmc
import server
import watcher

if __name__ == '__main__':
	t1 = threading.Thread(None, server.run)
	t2 = threading.Thread(None, watcher.run)
	t1.start()
	t2.start()

	monitor = xbmc.Monitor()

	while not monitor.abortRequested():

		if monitor.waitForAbort(1):
			break
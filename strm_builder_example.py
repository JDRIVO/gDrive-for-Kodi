# To be ran by the script that uploads files to Google Drive. Sync strms with resilio, syncthing etc. Install watchdog on Kodi.

import os
import sys
import subprocess
import shlex
import json

videoPath = sys.argv[1]
encryptedFilePath = sys.argv[2]
strmPath = sys.argv[3]

# videoPath = '/home/jack/movies/best movie 2000.mkv'
# encryptedFilePath = 'remote:/folder/RrtgFuvcxsWfKuFgGJ34VvcgfGFGWEWet'
# strmPath = '/home/jack/strm/movies/best movie 2000.strm'

cmd = 'ffprobe -v quiet -print_format json -show_format -show_streams'
args = shlex.split(cmd)
args.append(videoPath)
ffprobeOutput = subprocess.check_output(args).decode('utf-8')
ffprobeOutput = json.loads(ffprobeOutput)

if 'codec_name' in ffprobeOutput['streams'][0]:
	videoCodec = ffprobeOutput['streams'][0]['codec_name']
else:
	videoCodec = 'unknown'

videoWidth = str(ffprobeOutput['streams'][0]['width'])
videoHeight = str(ffprobeOutput['streams'][0]['height'])
videoDuration = str(ffprobeOutput['format']['duration'])
aspectRatio = str(float(videoWidth) / float(videoHeight) )
audioCodec = ffprobeOutput['streams'][1]['codec_name']
audioChannels = str(ffprobeOutput['streams'][1]['channels'])

cmd = 'rclone lsf --format i'
args = shlex.split(cmd)
args.append(encryptedFilePath)
fileID = subprocess.check_output(args).strip().decode('utf-8')

with open(strmPath, 'w+') as strm:
	# Every paramater is optional besides the filename (Google Drive File ID) - essential strm format is: plugin://plugin.video.gdrive/?mode=video&encfs=True&filename=7ctPNMUl4m8B4KBwY

	strm.write('''plugin://plugin.video.gdrive/?mode=video&encfs=True&video_codec=%s&video_width=%s&video_height=%s&video_duration=%s&aspect_ratio=%s
		   &audio_codec=%s&audio_channels=%s&filename=%s''' % (videoCodec, videoWidth, videoHeight, videoDuration, aspectRatio, audioCodec, audioChannels, fileID) )

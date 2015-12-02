from __future__ import absolute_import
from celery import shared_task
import os

# Asynchronous task
@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param

@shared_task
def video_encode(video_path):
	extensions = ('webm', 'ogv', 'mp4')
	new_video_path = video_path[1:].split('.')[-2]
	video_extension = video_path.split('.')[-1]
	for extension in extensions:
		if extension != video_extension:
			os.system("avconv -y -i {} -strict experimental {}.{}".format(video_path[1:], new_video_path, extension))
		else :
			new_video = new_video_path + '.' + extension
			os.system("avconv -y -i {} -strict experimental {}2.{}".format(video_path[1:], new_video_path, extension))
			os.system("mv {} {}".format(new_video_path +'2.'+ extension, new_video))
	#os.system("avconv -y -i {} -strict experimental {}.{}".format(video_path[1:], new_video_path))
	#os.system("avconv -y -i {} -strict experimental {}.{}".format(video_path[1:], new_video_path))
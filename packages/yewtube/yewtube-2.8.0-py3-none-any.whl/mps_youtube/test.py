from youtubesearchpython import *
import random

# This is how you display message
# g.message = "User {} not found.".format(c.y + user + c.w)


# Traceback (most recent call last):
#   File "/mnt/programmer/projects/yewtube-ng/yewtube/venv/lib/python3.10/site-packages/youtubesearchpython/handlers/componenthandler.py", line 89, in _getChannelSearchComponent
#     element = element["itemSectionRenderer"]["contents"][0]["videoRenderer"]
# KeyError: 'itemSectionRenderer'

import pafy, json

info = pafy.playlist_search('nfak')
print(info)


# channelsSearch = ChannelsSearch('BenLionelScott', limit = 10, region = 'US')
# videos = pafy.search_videos_from_channel('',pafy.channel_id_from_name('Ben lionel Scott')[0])
# print(videos)

# search = ChannelSearch('Do Not Give Up', pafy.channel_id_from_name('ben lionel scott')[0])
# print(search.result(mode = ResultMode.json))

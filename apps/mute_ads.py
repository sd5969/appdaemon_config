import appdaemon.plugins.hass.hassapi as hass
import sys
import threading

if sys.version_info < (3, 0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

import io

from PIL import Image
from urllib.parse import urlparse

# This script controls one or multiple RGB lights entity color based on the photo attribute of a media player entity
# Based on https://github.com/astone123/appdaemon-apps/blob/master/apps/music_lights.py
class mute_ads(hass.Hass):

    def initialize(self):
        for media_player in self.args["media_players"]:
            self.listen_state(self.handle_mute, media_player, attribute = "media_album_name")

    def handle_mute(self, entity, attribute, old, new, kwargs):
        self.log("old media_album_name: %s, new media_album_name: %s" % (old, new))
        if new != old:
            if new == "Advertisement":
                self.call_service("media_player/volume_mute", entity_id=entity, is_volume_muted=True)
            if old == "Advertisement":
                self.call_service("media_player/volume_mute", entity_id=entity, is_volume_muted=False)


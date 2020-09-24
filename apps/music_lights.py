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
class music_lights(hass.Hass):
 
  def initialize(self):
    self.lights = self.args["lights"]
    for media_player in self.args["media_players"]:
      for photo_attr in self.args["photo_attributes"]:
        self.listen_state(self.change_led_color, media_player, attribute = photo_attr)

  def change_led_color(self, entity, attribute, old, new, kwargs):
    if new != old:
      if new is None or new == "":
        rgb_colors = []
        for i in range(len(self.lights)):
          rgb_colors.append([255, 220, 151]) # approx 314 mireds
      elif not self.url_check(self.args["ha_url"] + new): # break (do nothing) if we don't have a real URL
          return
      else:
        rgb_colors = self.get_colors(self.args["ha_url"] + new)
      self.log(rgb_colors)
      for i in range(len(self.lights)):
        threading.Thread(target=self.set_light_rgb, args=(self.lights[i], rgb_colors[i])).start()

  def set_light_rgb(self, light, color):
    self.turn_on(light, rgb_color=color)

  def get_colors(self, url):
    fd = urlopen(url)
    f = io.BytesIO(fd.read())
    im = Image.open(f)
    palette = im.quantize(colors=len(self.lights)).getpalette()
    return self.extract_colors(palette, len(self.lights))

  def extract_colors(self, palette, colors):
    return [palette[i:i + 3] for i in range(0, colors * 3, 3)]

  # https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not/36283503#36283503
  @staticmethod
  def url_check(url):

    min_attr = ('scheme' , 'netloc')
    try:
      result = urlparse(url)
      if all([result.scheme, result.netloc]):
        return True
      else:
        return False
    except:
      return False

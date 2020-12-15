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
    self.listen_state(self.toggle_switch, self.args["toggle_switch"]) # listen for changing of the toggle switch
    self.lights = self.args["lights"]
    for media_player in self.args["media_players"]:
      for photo_attr in self.args["photo_attributes"]:
        self.listen_state(self.change_led_color, media_player, attribute = photo_attr) # listen for album cover changes for any of our media players in both photo attributes


  # handle changes to the toggle switch
  def toggle_switch(self, entity, attribute, old, new, kwargs):

    self.log("Toggle turned %s" % new)

    # set the color if something is playing
    if new == "on":
      for media_player in self.args["media_players"]:
        for photo_attr in self.args["photo_attributes"]:
          old_photo = "" # assume nothing was playing before
          new_photo = self.get_state(entity_id = media_player, attribute = photo_attr)
          # self.log(str(new_photo) + ", " + str(media_player) + ", " + str(photo_attr))
          if not new_photo is None and self.url_check(self.args["ha_url"] + new_photo):
            self.change_led_color(media_player, photo_attr, old_photo, new_photo, {})

    # set back to normal colors
    elif new == "off":
      all_lights_off = True
      for i in range(len(self.lights)):
        if self.get_state(entity_id = self.lights[i]) == "on":
          all_lights_off = False
      self.log("All lights off? %s" % all_lights_off)
      rgb_colors = []
      for i in range(len(self.lights)):
        rgb_colors.append([255, 220, 151]) # approx 314 mireds
      # change the colors
      self.log("Setting colors to %s" % rgb_colors)
      for i in range(len(self.lights)):
        threading.Thread(target=self.set_light_rgb, args=(self.lights[i], rgb_colors[i], all_lights_off)).start()


  # handle changes to a photo attribute
  def change_led_color(self, entity, attribute, old, new, kwargs):

    # only run if the toggle switch is enabled
    enabled = self.get_state(entity_id=self.args["toggle_switch"])
    self.log("Toggle is %s" % enabled)
    if not enabled == "on":
      return

    # do nothing if the picture isn't changing
    if new != old:

      # set colors equal to a nice lamp color when playback stops
      if new is None or new == "":
        rgb_colors = []
        for i in range(len(self.lights)):
          rgb_colors.append([255, 220, 151]) # approx 314 mireds

      # break (do nothing) if we don't have a real URL
      elif not self.url_check(self.args["ha_url"] + new):
          return

      # compute colors based on album art (new is the URL fragment to the picture)
      else:
        rgb_colors = self.get_colors(self.args["ha_url"] + new)

      # change the colors
      self.log("Setting colors to %s" % rgb_colors)
      for i in range(len(self.lights)):
        threading.Thread(target=self.set_light_rgb, args=(self.lights[i], rgb_colors[i], False)).start()

  # physically change the color of a light
  def set_light_rgb(self, light, color, turn_light_off):
    if not turn_light_off:
      self.turn_on(light, rgb_color=color)
    if turn_light_off:
      self.turn_on(light, rgb_color=color, brightness=1)
      self.turn_off(light)

  # algorithm to compute colors
  def get_colors(self, url):
    fd = urlopen(url)
    f = io.BytesIO(fd.read())
    im = Image.open(f)
    palette = im.quantize(colors=len(self.lights)).getpalette()
    return self.extract_colors(palette, len(self.lights))

  # transform colors into usable data format
  def extract_colors(self, palette, colors):
    return [palette[i:i + 3] for i in range(0, colors * 3, 3)]

  # helper to check for valid URL
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

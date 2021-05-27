import appdaemon.plugins.hass.hassapi as hass

GAIN = 0.1

class detect_noise(hass.Hass):

    def initialize(self):

      self.listen_state(self.detect_noise_response, self.args["noise_level_sensor"])

    def detect_noise_response(self, entity, attribute, old, new, kwargs):

      # max_volume = 0

      for media_player in self.args["media_players"]:

        # something is playing
        is_muted = self.get_state(entity_id=media_player, attribute="is_volume_muted")
        if is_muted == False:

          current_volume = self.get_state(entity_id=media_player, attribute="volume_level")
          # max_volume = max(current_volume, max_volume)

          # self.log("max volume %f", max_volume)

      for media_player in self.args["media_players"]:

        # something is playing
        is_muted = self.get_state(entity_id=media_player, attribute="is_volume_muted")
        if is_muted == False:

          current_volume = self.get_state(entity_id=media_player, attribute="volume_level")
          
          # self.log("%s", new == "True")
          if new == "True": # this is a string???

            set_volume = min(1, current_volume + GAIN)
            self.call_service("media_player/volume_set", entity_id=media_player, volume_level=set_volume)

          else:

            set_volume = max(0, current_volume - GAIN)
            self.call_service("media_player/volume_set", entity_id=media_player, volume_level=set_volume)

          # self.log("set volume %f", set_volume)

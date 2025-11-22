import appdaemon.plugins.hass.hassapi as hass

class control_volume(hass.Hass):

    def initialize(self):

      for (i, source) in enumerate(self.args["volume_up"]["trigger_sources"]):

        kwargs = {}
        kwargs[self.args["volume_up"]["event_data_keys"][i]] = self.args["volume_up"]["event_data_values"][i]

        self.listen_event(self.change_volume, event=source, increase_volume=True, **kwargs)

      for (j, source) in enumerate(self.args["volume_down"]["trigger_sources"]):

        kwargs = {}
        kwargs[self.args["volume_down"]["event_data_keys"][j]] = self.args["volume_down"]["event_data_values"][j]

        self.listen_event(self.change_volume, event=source, increase_volume=False, **kwargs)

    def change_volume(self, event, attributes, kwargs):

      max_volume = 0

      for media_player in self.args["media_players"]:

        # something is playing
        is_muted = self.get_state(entity_id=media_player, attribute="is_volume_muted")
        # is_playing = not not self.get_state(entity_id=media_player, attribute="media_title")
        is_playing = (self.get_state(entity_id=media_player) == "playing")

        # self.log("%s is_playing: %s", media_player, is_playing)

        if not is_muted and is_playing:

          current_volume = self.get_state(entity_id=media_player, attribute="volume_level")
          max_volume = max(current_volume, max_volume)

          # self.log("max volume %f", max_volume)

      for media_player in self.args["media_players"]:

        # something is playing
        is_muted = self.get_state(entity_id=media_player, attribute="is_volume_muted")
        # is_playing = not not self.get_state(entity_id=media_player, attribute="media_title")
        is_playing = (self.get_state(entity_id=media_player) == "playing")
        if not is_muted and is_playing:

          if kwargs["increase_volume"]:

            set_volume = min(1, max_volume * (1 + self.args["volume_increment"]))
            self.call_service("media_player/volume_set", entity_id=media_player, volume_level=set_volume)

          else:

            set_volume = max(0, max_volume * (1 - self.args["volume_increment"]))
            self.call_service("media_player/volume_set", entity_id=media_player, volume_level=set_volume)

          self.log("set volume %f", set_volume)

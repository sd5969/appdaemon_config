import appdaemon.plugins.hass.hassapi as hass

class control_volume(hass.Hass):

    def initialize(self):
      for (i, source) in enumerate(self.args["volume_up"]["trigger_sources"]):
        kwargs = {}
        kwargs[self.args["volume_up"]["event_data_keys"][i]] = self.args["volume_up"]["event_data_values"][i]
        self.listen_event(self.change_volume, event=source, increase_volume=False, **kwargs)
      for (j, source) in enumerate(self.args["volume_down"]["trigger_sources"]):
        kwargs = {}
        kwargs[self.args["volume_down"]["event_data_keys"][j]] = self.args["volume_down"]["event_data_values"][j]
        self.listen_event(self.change_volume, event=source, increase_volume=True, **kwargs)

    def change_volume(self, event, attributes, kwargs):
      for media_player in self.args["media_players"]:
          is_muted = self.get_state(entity_id=media_player, attribute="is_volume_muted")

          # something is playing
          if is_muted == False:
            current_volume = self.get_state(entity_id=media_player, attribute="volume_level")
            if kwargs["increase_volume"]:
              self.call_service("media_player/volume_up", entity_id=media_player)
            else:
              self.call_service("media_player/volume_down", entity_id=media_player)

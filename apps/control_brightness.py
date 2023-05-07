import appdaemon.plugins.hass.hassapi as hass

class control_brightness(hass.Hass):

    def initialize(self):

      for (i, source) in enumerate(self.args["brightness_up"]["trigger_sources"]):

        kwargs = {}
        kwargs[self.args["brightness_up"]["event_data_keys"][i]] = self.args["brightness_up"]["event_data_values"][i]

        self.listen_event(self.change_brightness, event=source, increase_brightness=True, **kwargs)

      for (j, source) in enumerate(self.args["brightness_down"]["trigger_sources"]):

        kwargs = {}
        kwargs[self.args["brightness_down"]["event_data_keys"][j]] = self.args["brightness_down"]["event_data_values"][j]

        self.listen_event(self.change_brightness, event=source, increase_brightness=False, **kwargs)

    def change_brightness(self, event, attributes, kwargs):

      for light in self.args["lights"]:

        # light is on
        is_on = self.get_state(entity_id=light)
        if is_on == "on":

          current_brightness = self.get_state(entity_id=light, attribute="brightness")

          if kwargs["increase_brightness"]:

            set_brightness = min(255, current_brightness + 60)
            self.call_service("light/turn_on", entity_id=light, brightness=set_brightness)

          else:

            set_brightness = max(0, current_brightness - 60)
            self.call_service("light/turn_on", entity_id=light, brightness=set_brightness)

          # self.log("set brightness %f", set_brightness)

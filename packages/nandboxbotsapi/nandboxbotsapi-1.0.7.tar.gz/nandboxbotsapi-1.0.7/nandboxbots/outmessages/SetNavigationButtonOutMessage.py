import json

from nandboxbots.outmessages.OutMessage import OutMessage


class SetNavigationButtonOutMessage(OutMessage):
    __KEY_NAVIGATION_BUTTONS = "navigation_buttons"

    navigation_buttons = []

    def __init__(self):
        self.method = "setNavigationButton"

    def to_json_obj(self):
        _, dictionary = super(SetNavigationButtonOutMessage, self).to_json_obj()

        if self.navigation_buttons is not None:
            dictionary[self.__KEY_NAVIGATION_BUTTONS] = self.navigation_buttons

        return json.dumps(dictionary), dictionary
    

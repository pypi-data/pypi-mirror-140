import json

from nandboxbots.outmessages.OutMessage import OutMessage


class DeleteWhiteListOutMessage(OutMessage):
    __KEY_USERS = "users"

    users = []

    def __init__(self):
        self.method = "deleteWhitelist"

    def to_json_obj(self):
        _, dictionary = super(DeleteWhiteListOutMessage, self).to_json_obj()

        if self.users is not None:
            dictionary[self.__KEY_USERS] = self.users

        return json.dumps(dictionary), dictionary
    
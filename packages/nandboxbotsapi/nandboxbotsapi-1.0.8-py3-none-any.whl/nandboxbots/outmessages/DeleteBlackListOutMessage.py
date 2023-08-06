import json

from nandboxbots.outmessages.OutMessage import OutMessage


class DeleteBlackListOutMessage(OutMessage):
    __KEY_USERS = "users"

    users = []

    def __init__(self):
        self.method = "deleteBlacklist"

    def to_json_obj(self):
        _, dictionary = super(DeleteBlackListOutMessage, self).to_json_obj()

        if self.users is not None:
            dictionary[self.__KEY_USERS] = self.users

        return json.dumps(dictionary), dictionary
    
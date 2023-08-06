import json

from nandboxbots.data.Chat import Chat
from nandboxbots.data.User import User


class ChatMember:
    __KEY_CHAT_MEMBER = "chatMember"
    __KEY_USER = "user"
    __KEY_CHAT = "chat"
    __KEY_TYPE = "type"
    __KEY_MEMBER_SINCE = "member_since"
    __KEY_STATUS = "status"
    __KEY_TAGS = "tags"
    __KEY_ACCOUNT_TYPE = "account_type"
    __KEY_MSISDN = "msisdn"

    user = None
    chat = None
    type = None
    member_since = None
    status = None
    tags = []
    account_type = None
    msisdn = None

    def __init__(self, dictionary):

        chat_member_dict = dictionary[self.__KEY_CHAT_MEMBER] if self.__KEY_CHAT_MEMBER in dictionary.keys() else {}

        self.user = User(chat_member_dict.get(self.__KEY_USER, None))
        self.chat = Chat(chat_member_dict.get(self.__KEY_CHAT, None))
        self.type = str(chat_member_dict[self.__KEY_TYPE]) if self.__KEY_TYPE in chat_member_dict.keys() else None
        self.member_since = int(chat_member_dict[self.__KEY_MEMBER_SINCE]) if self.__KEY_MEMBER_SINCE in chat_member_dict.keys() else None
        self.status = str(chat_member_dict[self.__KEY_STATUS]) if self.__KEY_STATUS in chat_member_dict.keys() else None
        self.tags = chat_member_dict[self.__KEY_TAGS] if self.__KEY_TAGS in chat_member_dict.keys() else None
        self.account_type = chat_member_dict[self.__KEY_ACCOUNT_TYPE] if self.__KEY_ACCOUNT_TYPE in chat_member_dict.keys() else None
        self.msisdn = chat_member_dict[self.__KEY_MSISDN] if self.__KEY_MSISDN in chat_member_dict.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if not self.tags == []:
            dictionary[self.__KEY_TAGS] = self.tags
        if self.user is not None:
            _, user_dict = self.user.to_json_obj()
            dictionary[self.__KEY_USER] = user_dict
        if self.chat is not None:
            _, chat_dict = self.chat.to_json_obj()
            dictionary[self.__KEY_CHAT] = chat_dict
        if self.type is not None:
            dictionary[self.type] = self.type
        if self.member_since is not None:
            dictionary[self.__KEY_MEMBER_SINCE] = self.member_since
        if self.status is not None:
            dictionary[self.__KEY_STATUS] = self.status
        if self.account_type is not None:
            dictionary[self.__KEY_ACCOUNT_TYPE] = self.account_type
        if self.msisdn is not None:
            dictionary[self.__KEY_MSISDN] = self.msisdn

        return json.dumps(dictionary), dictionary

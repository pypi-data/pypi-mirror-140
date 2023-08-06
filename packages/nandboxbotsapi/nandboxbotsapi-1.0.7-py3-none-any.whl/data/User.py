import json

from nandboxbots.data.Photo import Photo


class User:
    __KEY_ID = "id"
    __KEY_NAME = "name"
    __KEY_TERMINAL = "terminal"
    __KEY_TYPE = "type"
    __KEY_IS_BOT = "is_bot"
    __KEY_VERSION = "version"
    __KEY_LAST_SEEN = "last_seen"
    __KEY_STATUS = "status"
    __KEY_PHOTO = "photo"
    __KEY_PROFILE = "profile"
    __KEY_SHORT_NAME = "short_name"

    id = None
    name = None
    version = None
    terminal = None
    type = None
    is_bot = False
    last_seen = None
    status = None
    profile = None
    photo = None
    short_name = None

    def __init__(self, dictionary):
        # print(str(dictionary))
        self.id = str(dictionary[self.__KEY_ID]) if self.__KEY_ID in dictionary.keys() else None
        self.name = str(dictionary[self.__KEY_NAME]) if self.__KEY_NAME in dictionary.keys() else None
        self.version = str(dictionary[self.__KEY_VERSION]) if self.__KEY_VERSION in dictionary.keys() else None
        self.terminal = str(dictionary[self.__KEY_TERMINAL]) if self.__KEY_TERMINAL in dictionary.keys() else None
        self.type = str(dictionary[self.__KEY_TYPE]) if self.__KEY_TYPE in dictionary.keys() else None
        self.is_bot = bool(dictionary[self.__KEY_IS_BOT]) if self.__KEY_IS_BOT in dictionary.keys() else None
        self.last_seen = str(dictionary[self.__KEY_LAST_SEEN]) if self.__KEY_LAST_SEEN in dictionary.keys() else None
        self.status = str(dictionary[self.__KEY_STATUS]) if self.__KEY_STATUS in dictionary.keys() else None
        self.profile = str(dictionary[self.__KEY_PROFILE]) if self.__KEY_PROFILE in dictionary.keys() else None

        self.photo = Photo(dictionary.get(self.__KEY_PHOTO, {}))

        self.short_name = str(dictionary[self.__KEY_SHORT_NAME]) if self.__KEY_SHORT_NAME in dictionary.keys() else None

    def to_json_obj(self):
        dictionary = {}

        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.version is not None:
            dictionary[self.__KEY_VERSION] = self.version
        if self.terminal is not None:
            dictionary[self.__KEY_TERMINAL] = self.terminal
        if self.type is not None:
            dictionary[self.__KEY_TYPE] = self.type
        if self.is_bot is not None:
            dictionary[self.__KEY_IS_BOT] = self.is_bot
        if self.last_seen is not None:
            dictionary[self.__KEY_LAST_SEEN] = self.last_seen
        if self.status is not None:
            dictionary[self.__KEY_STATUS] = self.status
        if self.profile is not None:
            dictionary[self.__KEY_PROFILE] = self.profile
        if self.photo is not None:
            _, photo_dict = self.photo.to_json_obj()
            dictionary[self.__KEY_PHOTO] = photo_dict
        if self.short_name is not None:
            dictionary[self.__KEY_SHORT_NAME] = self.short_name

        return json.dumps(dictionary), dictionary

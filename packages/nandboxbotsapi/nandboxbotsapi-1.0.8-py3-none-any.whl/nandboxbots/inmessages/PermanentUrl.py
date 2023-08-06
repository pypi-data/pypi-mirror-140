import json


class PermanentUrl:
    __KEY_FILE = "file"
    __KEY_URL = "url"
    __KEY_PARAM1 = "param1"

    file = None
    url = None
    param1 = None

    def __init__(self, dictionary):
        self.url = str(dictionary[self.__KEY_URL]) if self.__KEY_URL in dictionary.keys() else None
        self.file = str(dictionary[self.__KEY_FILE]) if self.__KEY_FILE in dictionary.keys() else None
        self.param1 = str(dictionary[self.__KEY_PARAM1]) if self.__KEY_PARAM1 in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.url is not None:
            dictionary[self.__KEY_URL] = self.url
        if self.file is not None:
            dictionary[self.__KEY_FILE] = self.file
        if self.param1 is not None:
            dictionary[self.__KEY_PARAM1] = self.param1

        return json.dumps(dictionary), dictionary

import json


class Data:
    __KEY_PATTERN = "pattern"
    __KEY_EXAMPLE = "example"

    pattern = None
    example = None

    def __init__(self, dictionary=None):
        if dictionary is None or dictionary == {}:
            return
        self.pattern = str(dictionary[self.__KEY_PATTERN]) if self.__KEY_PATTERN in dictionary.keys() else None
        self.example = str(dictionary[self.__KEY_EXAMPLE]) if self.__KEY_EXAMPLE in dictionary.keys() else None

    def to_json_obj(self):

        dictionary = {}

        if self.pattern is not None:
            dictionary[self.__KEY_PATTERN] = self.pattern
        if self.example is not None:
            dictionary[self.__KEY_EXAMPLE] = self.example

        return json.dumps(dictionary), dictionary

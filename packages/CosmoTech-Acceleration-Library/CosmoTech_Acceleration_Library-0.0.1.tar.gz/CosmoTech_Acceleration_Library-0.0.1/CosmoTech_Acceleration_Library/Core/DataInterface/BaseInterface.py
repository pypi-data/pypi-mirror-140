# Copyright (c) Cosmo Tech corporation.
# Licensed under the MIT license.
import json


class BaseInterface:

    def __init__(self):

        self.content = []

    def add_element(self, element: dict):
        to_append = dict()
        for key, value in element:
            try:
                converted_value = json.loads(value)
            except json.decoder.JSONDecodeError:
                converted_value = value
            to_append[key] = converted_value
        self.content.append(element)

    def __iter__(self):
        return self.content.__iter__()

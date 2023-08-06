# Copyright (c) Cosmo Tech corporation.
# Licensed under the MIT license.
import csv
import os
from ...DataInterface.BaseInterface import BaseInterface

class CSVReader:

    def refresh(self):
        self.interface = BaseInterface()
        if os.path.exists(self.file_path):
            for element in csv.DictReader(open(self.file_path, "r")):
                self.interface.add_element(element)

    def __init__(self, file_path):
        self.interface = None
        self.file_path = file_path
        self.refresh()

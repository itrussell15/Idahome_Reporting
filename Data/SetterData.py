# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:49:52 2022

@author: Schmuck
"""

from ReportableData import ReportableData

class _SetterData(ReportableData):
    
    def __init__(self, name, raw_data, previous_weeks = 6):
        super().__init__(name, raw_data, previous_weeks)
        
class SetterInvidualData(_SetterData):

    def __init__(self, setter_name, data):
        super().__init__(setter_name, data)
        
class SetterOfficeData(_SetterData):

    def __init__(self, data):
        super().__init__("Office", data)
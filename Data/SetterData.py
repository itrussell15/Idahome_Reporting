# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:49:52 2022

@author: Schmuck
"""

from ReportableData import ReportableData

class _SetterData(ReportableData):
    
    def __init__(self, name, raw_data, previous_weeks = 6):
        super().__init__(name, raw_data, previous_weeks)
        
        self.numLeads = len(self.leads)
        self.numSigns = self._getGroupedTotal("Signed", self._status)
        self.numPitched = self._getPitched()
        
        self.numNoShow = self._getGroupedTotal("No Show", self._status) + \
            self._getGroupedTotal("Canceled", self._status)
        
        self.pitchRatio = self._potentialDivisionError(self.numPitched, self.numLeads)
        self.closeRatio = self._potentialDivisionError(self.numSigns, self.numLeads)
        self.cancelRatio = self._potentialDivisionError(self.numNoShow, self.numLeads)
                
class SetterInvidualData(_SetterData):

    def __init__(self, setter_name, data):
        super().__init__(setter_name, data)
        
class SetterOfficeData(_SetterData):

    def __init__(self, data):
        super().__init__("Office", data)
        self.leads = self.leads[self.leads["Setter"] != "No Setter"]
        

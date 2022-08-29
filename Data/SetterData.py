# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:49:52 2022

@author: Schmuck
"""
if __name__ != "__main__":
    from ReportableData import CustomerData
else:    
    from Data.ReportableData import CustomerData
    
import numpy as np

class _SetterData(CustomerData):
    
    def __init__(self, name, raw_data, prepForReport):
        super().__init__(name, raw_data, False)
        
        self.leads = self.leads.dropna(subset = ["setter"])    
        
        if prepForReport:
            self._reportPrep()
        
        self.numLeads = len(self.leads)
        self.numSigns = self._getGroupedTotal("Signed", self._status)
        self.numPitched = self._getPitched()
        
        self.numNoShow = self._getGroupedTotal("No Show", self._status) + \
            self._getGroupedTotal("Canceled", self._status)
        
        # print(self.numLeads)
        # print(self.numPitched)
        
        self.pitchRatio = self._potentialDivisionError(self.numPitched, self.numLeads)
        self.closeRatio = self._potentialDivisionError(self.numSigns, self.numLeads)
        self.cancelRatio = self._potentialDivisionError(self.numNoShow, self.numLeads)
        
    def scrapeForAppt(self, x):
        if x != "Null":
            return " ".join((str(x).split(" ")[:-1]))
                
class SetterInvidualData(_SetterData):

    def __init__(self, setter_name, data, prepForReport):
        super().__init__(setter_name, data, prepForReport)
        self.leads.drop("setter", axis = 1, inplace = True)
        
class SetterOfficeData(_SetterData):

    def __init__(self, data, prepForReport):
        super().__init__("Office", data, prepForReport)
    
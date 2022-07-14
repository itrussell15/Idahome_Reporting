# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:49:52 2022

@author: Schmuck
"""

from Data.ReportableData import ReportableData
import numpy as np

class _SetterData(ReportableData):
    
    def __init__(self, name, raw_data, previous_weeks):
        super().__init__(name, raw_data, previous_weeks)
        
        self.numLeads = len(self.leads)
    
        self.numSigns = self._getGroupedTotal("Signed", self._status)
        self.numPitched = self._getPitched()
        
        self.numNoShow = self._getGroupedTotal("No Show", self._status) + \
            self._getGroupedTotal("Canceled", self._status)
        
        self.pitchRatio = self._potentialDivisionError(self.numPitched, self.numLeads)
        self.closeRatio = self._potentialDivisionError(self.numSigns, self.numLeads)
        self.cancelRatio = self._potentialDivisionError(self.numNoShow, self.numLeads)
        
        self.leads["Next Appt"] = self.leads["Next Appointment"].apply(self.scrapeForAppt)

    def scrapeForAppt(self, x):
        if x != "Null":
            return " ".join((str(x).split(" ")[:-1]))
                
class SetterInvidualData(_SetterData):

    def __init__(self, setter_name, data):
        super().__init__(setter_name, data)
        
        
class SetterOfficeData(_SetterData):

    def __init__(self, data):
        super().__init__("Office", data)
        self.leads = self.leads[self.leads["Setter"] != "No Setter"]
        
        self.setters = self.leads["Setter"].unique()
        self.closers = self.leads["Lead Owner"].unique()
        self.leads = self.leads[~self.leads.isin(self.closers)]
        self.leads = self.leads.dropna(subset = ["Setter"])
        self.leads["Setter"] = self.leads["Setter"].apply(self.cleanNames)
 
    def cleanNames(self, x, length = 18):
        return str(x) if len(str(x)) < length else "{}..".format(x[:length-1].strip())

    
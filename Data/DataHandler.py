# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""

import sys

import pandas as pd
import os, datetime
import matplotlib.pyplot as plt
import matplotlib

from Data.CloserData import InvidualData, OfficeData
from Data.SetterData import SetterInvidualData, SetterOfficeData

class DataHandler:

    def __init__(self, data_path):
        self._df = pd.read_excel(data_path)
        self._df["Lead Status"].fillna("No Dispo", inplace = True)
        self._df["Lead Source"].fillna("No Lead Source", inplace = True)
        self._df["Lead Owner"].fillna("No Owner", inplace = True)
        self._df["Setter"].fillna("No Setter", inplace = True)
        self._df["Office"].fillna("No Office", inplace = True)
        
        self.closers = self._getClosers()
        self.setters = self._getSetters()
        
    # Only used to get the names for all of the data, NOT the time period
    def _getClosers(self):
        return self._getUnique("Lead Owner")
    
    # Only used to get the names for all of the data, NOT the time period
    def _getSetters(self):
        return list(set(self._getUnique("Setter")) - set(self.closers))
    
    def _getUnique(self, column):
        return self._df[column].unique()
    
    def getCloserData(self, name = None, previous_weeks = 6):
        if name:
            if name in self._getClosers():
                closerData = self._df.loc[self._df["Lead Owner"] == name].copy()
                closerData.drop("Lead Owner", axis = 1, inplace = True)
                return InvidualData(name, closerData, previous_weeks)
            else:
                raise KeyError("{} has no leads in this data".format(name))
        else:
            officeData = OfficeData(self._df.copy())
            # Sets closers and setters for time period
            self.closers = officeData.closers
            self.setters = list(set(officeData.setters) - set(self.closers))
            return officeData
        
    def getSetterData(self, name = None, previous_weeks = 6):
        if name:
            if name in self._getSetters():
                setterData = self._df.loc[self._df["Setter"] == name].copy()
                setterData.drop("Setter", axis = 1, inplace = True)
                return SetterInvidualData(name, setterData, previous_weeks)
            else:
                raise ValueError("Not a valid setter name")
        else:
            officeData = SetterOfficeData(self._df.copy())
            # Sets closers and setters for time period
            self.closers = officeData.closers
            self.setters = list(set(officeData.setters) - set(self.closers))
            return officeData

if __name__ == "__main__":
    data = DataHandler(os.getcwd() + "/Data.xlsx")
    # out = data.getCloserData()
    # out.closerLeadStatus()
    setter = data.getSetterData()
    
    
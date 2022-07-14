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

if __name__ == "__main__":
    from CloserData import InvidualData, OfficeData
    from SetterData import SetterInvidualData, SetterOfficeData
    from EnerfloWrapper import EnerfloWrapper
else:
    from Data.CloserData import InvidualData, OfficeData
    from Data.SetterData import SetterInvidualData, SetterOfficeData
    from Data.EnerfloWrapper import EnerfloWrapper

class DataHandler:

    def __init__(self, previous_weeks = 6):
        # self._df = pd.read_excel(data_path)
        wrapper = EnerfloWrapper()
        self._df = wrapper.getCustomers(pageSize = 100, previous_weeks = previous_weeks)
        
        # self._df["lead_status"].fillna("No Dispo", inplace = True)
        # self._df["lead_source"].fillna("No Lead Source", inplace = True)
        # self._df["owner"].fillna("No Owner", inplace = True)
        # self._df["setter"].fillna("No Setter", inplace = True)
        
        # self.closers = self._getClosers()
        # self.setters = self._getSetters()
        
        print(self._df)
        
    # Only used to get the names for all of the data, NOT the time period
    def _getClosers(self):
        return self._getUnique("owner")
    
    # Only used to get the names for all of the data, NOT the time period
    def _getSetters(self):
        return list(set(self._getUnique("setter")) - set(self.closers))
    
    def _getUnique(self, column):
        return self._df[column].unique()
    
    def getCloserData(self, name = None):
        if name:
            if name in self._getClosers():
                closerData = self._df.loc[self._df["owner"] == name].copy()
                closerData.drop("owner", axis = 1, inplace = True)
                return InvidualData(name, closerData)
            else:
                raise KeyError("{} has no leads in this data".format(name))
        else:
            officeData = OfficeData(self._df.copy())
            # Sets closers and setters for time period
            self.closers = officeData.closers
            self.setters = list(set(officeData.setters) - set(self.closers))
            return officeData
        
    def getSetterData(self, name = None):
        if name:
            if name in self._getSetters():
                setterData = self._df.loc[self._df["setter"] == name].copy()
                setterData.drop("setter", axis = 1, inplace = True)
                return SetterInvidualData(name, setterData)
            else:
                raise ValueError("Not a valid setter name")
        else:
            officeData = SetterOfficeData(self._df.copy())
            # Sets closers and setters for time period
            self.closers = officeData.closers
            self.setters = list(set(officeData.setters) - set(self.closers))
            return officeData

if __name__ == "__main__":
    # sys.path.append("Data")
    
    data = DataHandler(previous_weeks = 1)
    # out = data.getCloserData()
    # out.closerLeadStatus()
    setter = data.getSetterData()
    
    
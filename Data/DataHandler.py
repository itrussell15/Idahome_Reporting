# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""



import pandas as pd
import os, datetime
import matplotlib.pyplot as plt
import matplotlib

from CloserData import InvidualData, OfficeData
from SetterData import SetterInvidualData, SetterOfficeData

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
        
    def _getClosers(self):
        return self._getUnique("Lead Owner")
    
    def _getSetters(self):
        return self._getUnique("Setter")
    
    def _getUnique(self, column):
        return self._df[column].unique()
    
    def getCloserData(self, name = None):
        if name:
            if name in self._getClosers():
                closerData = self._df.loc[self._df["Lead Owner"] == name].copy()
                closerData.drop("Lead Owner", axis = 1, inplace = True)
                return InvidualData(name, closerData)
            else:
                raise KeyError("{} has no leads in this data".format(name))
        else:
            return OfficeData(self._df.copy())
        
    def getSetterData(self, name = None):
        
        if name:
            
            if name in self._getSetters():
                setterData = self._df.loc[self._df["Setter"] == name].copy()
                setterData.drop("Setter", axis = 1, inplace = True)
                return SetterInvidualData(name, setterData)
        else:
            return SetterOfficeData(self._df.copy())

if __name__ == "__main__":
    data = DataHandler(os.getcwd() + "/Data.xlsx")
    # out = data.getCloserData()
    # out.closerLeadStatus()
    setter = data.getSetterData()
    
    
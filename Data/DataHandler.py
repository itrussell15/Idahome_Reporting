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
import logging
from global_functions import resource_path

# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 100)
# pd.set_option('display.width', 300)

if __name__ == "__main__":
    from CloserData import InvidualData, OfficeData
    from SetterData import SetterInvidualData, SetterOfficeData
    from EnerfloWrapper import EnerfloWrapper
    from ReportableData import ReportableData
else:
    from CloserData import InvidualData, OfficeData
    from SetterData import SetterInvidualData, SetterOfficeData
    from EnerfloWrapper import EnerfloWrapper

class DataHandler:

    def __init__(self, previous_weeks = 6):
        
        self.setupLogging()
        logging.info("Program Started @ {}".format(datetime.datetime.now()))
        
        wrapper = EnerfloWrapper()
        self._df = wrapper.getCustomers(pageSize = 200, previous_weeks = previous_weeks)
               
        self.closers = self._getClosers()
        self.setters = self._getSetters()
        
        logging.info("{} Closers and {} Setter found in this data".format(len(self.closers), len(self.setters)))
    
    def setupLogging(self):
        log_format = '%(levelname)s--%(filename)s-line %(lineno)s: %(message)s'
        logging.basicConfig(
            level = logging.INFO,
            format = log_format,
            filename = resource_path("master.log"),
            force = True,
            filemode = "w"
            )
        logging.getLogger(__name__)
    
    # Finds unique closers in the df
    def _getClosers(self):
        return self._getUnique("owner")
    
    # Finds setters closers in the df
    def _getSetters(self):
        return list(set(self._getUnique("setter")) - set(self.closers))
    
    def _getUnique(self, column):
        return self._df[column].unique()
    
    def getReportableData(self):
        return ReportableData("Test", self._df, prepForReport = True)
    
    def getCloserData(self, name = None, prepForReport = True):
        if name:
            if name in self._getClosers():
                closerData = self._df.loc[self._df["owner"] == name].copy()
                # closerData.drop("owner", axis = 1, inplace = True)
                return InvidualData(name, closerData, prepForReport)
            else:
                logging.warn("Closer {} has no leads in data".format(name))
                raise KeyError("{} has no leads in this data".format(name))
        else:
            officeData = OfficeData(self._df.copy(), prepForReport)
            return officeData
        
    def getSetterData(self, name = None, prepForReport = True):
        if name:
            if name in self._getSetters():
                setterData = self._df.loc[self._df["setter"] == name].copy()
                return SetterInvidualData(name, setterData, prepForReport)
            else:
                logging.warn("Setter {} has no leads in this data".format(name))
                raise ValueError("Not a valid setter name")
        else:
            officeData = SetterOfficeData(self._df.copy(), prepForReport)
            return officeData

if __name__ == "__main__":
    data = DataHandler(previous_weeks = 1)
    # test = data.getReportableData()
    # closer = data.getCloserData("Zach Trussell")
    setter = data.getSetterData()

    # print(setter.leads.head(15))
    
    
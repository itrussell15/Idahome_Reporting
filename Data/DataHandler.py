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
    from ReportableData import CustomerData, InstallData
else:
    from CloserData import InvidualData, OfficeData
    from SetterData import SetterInvidualData, SetterOfficeData
    from EnerfloWrapper import EnerfloWrapper

class DataHandler:

    def __init__(self, previous_weeks = 6, page_size = 200):
        
        self.setupLogging()
        logging.info("Program Started @ {}".format(datetime.datetime.now()))
        
        self.wrapper = EnerfloWrapper(perPageRequest = page_size)
        self.previous_weeks = previous_weeks
    
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

# %% Private Calls

    # # Finds unique closers in the df
    # def _getClosers(self, df):
    #     return self._getUnique("owner", df)
    
    # # Finds setters closers in the df
    # def _getSetters(self, df):
    #     return list(set(self._getUnique("setter")) - set(self.closers))
    
    # def _getUnique(self, column, df):
    #     return df[column].unique()
    
    def _queryForCustomers(self):
        df = self.wrapper.getCustomers(previous_weeks = self.previous_weeks)
        logging.info("Queried for Customers")
        # self.closers = self._getClosers(df)
        # self.setters = self._getSetters(df)
        # logging.info("{} Closers and {} Setter found in this data".format(len(self.closers), len(self.setters)))
        return df
    
    # def _queryForInstalls(self):
    #     df = self.wrapper.getInstalls(previous_weeks = self.previous_weeks)
        
    
# %% CustomerData Pulls

    def getReportableData(self):
        df = self._queryForCustomers()
        return CustomerData("Test", df, prepForReport = True)
    
    def getCloserData(self, name = None, prepForReport = True):
        df = self._queryForCustomers()
        if name:
            if name in self._getClosers():
                closerData = df.loc[df["owner"] == name].copy()
                return InvidualData(name, closerData, prepForReport)
            else:
                logging.warn("Closer {} has no leads in data".format(name))
                raise KeyError("{} has no leads in this data".format(name))
        else:
            officeData = OfficeData(df.copy(), prepForReport)
            return officeData
        
    def getSetterData(self, name = None, prepForReport = True):
        df = self._queryForCustomers()
        if name:
            if name in self._getSetters():
                setterData = df.loc[df["setter"] == name].copy()
                return SetterInvidualData(name, setterData, prepForReport)
            else:
                logging.warn("Setter {} has no leads in this data".format(name))
                raise ValueError("Not a valid setter name")
        else:
            officeData = SetterOfficeData(df.copy(), prepForReport)
            return officeData

# %% InstallData Pulls

    # def getInstallData(self, name = None):        
    #     return InstallData(self)

# %% Main
if __name__ == "__main__":
    data = DataHandler(previous_weeks = 1)
    installs = data.getInstallData()
    
    
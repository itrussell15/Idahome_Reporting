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
from enum import Enum

from global_functions import resource_path

import Customers
import Installs


# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 100)
# pd.set_option('display.width', 300)

# if __name__ == "__main__":
#     from CloserData import InvidualData, OfficeData
#     from SetterData import SetterInvidualData, SetterOfficeData
#     from EnerfloWrapper import EnerfloWrapper
#     from ReportableData import CustomerData, InstallData
# else:
#     from CloserData import InvidualData, OfficeData
#     from SetterData import SetterInvidualData, SetterOfficeData
#     from EnerfloWrapper import EnerfloWrapper

import EnerfloWrapper

class DataHandler:

    def __init__(self, previous_weeks = 6, page_size = 200):
        self.previous_weeks = previous_weeks
        self.page_size = page_size
        
        self.setupLogging()
        logging.info("Program Started @ {}".format(datetime.datetime.now()))
        
        self._customers = False
        self._installs = pd.DataFrame()
    
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
        
    @property
    def closers(self):
        return self.customers.closers
    
    @property
    def setters(self):
        return self.customers.setters

# %% Data Grabs

    def _collectCustomers(self):
        customers = EnerfloWrapper.Customers(
            perPageRequest = self.page_size,
            previous_weeks = self.previous_weeks)
        return customers
    
    @property
    def customers(self):
        if not self._customers:
            self._customers = self._collectCustomers()
        return self._customers
    
    def getCloser(self, name = None):
        if name:
            return Customers.IndvCloserData(name, self.customers)
        else:
            return Customers.OfficeCloserData(self.customers)
    
    def getSetter(self, name = None):
        if name:
            return Customers.IndvSetterData(name, self.customers)
        else:
            return Customers.OfficeSetterData(self.customers)
    
    def _collectInstalls(self):
        installs = EnerfloWrapper.Installs(
            perPageRequest = self.page_size)
        return installs

    @property
    def installs(self):
        if self._installs.empty:
            self._installs = self._collectInstalls()
        return self._installs
    
    def getInstalls(self):
        return Installs.Installs(None, self.installs)
    
    def attachInstalls(self, data):
        self._installs = data
    
class JOB_TYPE(Enum):
    CLOSER = 1,
    SETTER = 2
    

# %% InstallData Pulls

    # def getInstallData(self, name = None):        
    #     return InstallData(self)

# %% Main
if __name__ ==  "__main__":
    data = DataHandler(previous_weeks = 1)
    # setter = data.getSetter("Kyle Wagner")
    closer = data.getCloser("Darren Phillips")
    print(closer)
    # office = data.getOffice(JOB_TYPE.SETTER)
    
    
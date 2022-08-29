# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:02:01 2022

@author: Schmuck
"""

# ***PURPOSE****
# House Metadata and KPIs for data that has been passed into it.
# Should not 

import datetime
import pandas as pd
import logging
import json

# from DataHandler import DataHandler

class BaseData:
    
    def __init__(self, data_obj):
        self._data = self.dataImporter(data_obj)
        
    def dataImporter(self, data_obj):
        this_type = type(data_obj)
        logging.info("Data gathered with {}".format(this_type))
        if this_type == pd.core.frame.DataFrame:
            return self._importDataFrame(data_obj)
        elif this_type == str:
            return self._importFile(data_obj)
        else:
            # DataHandler section
            if self.__class__.__name__ == "Installs":
                return data_obj.installs.data
            else:
                return data_obj.customers.data
    
    def _getUnique(self, column):
        data = self._data[column].dropna()
        return data.unique()
    
    @property
    def closers(self):
        return self._getUnique("closer")
    
    @property
    def setters(self):
        return self._getUnique("setter")
    
    @property
    def data(self):
        return self._data
            
    def _importFile(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data)
        return self._importDataFrame(df)
    
    def _importDataFrame(self, data):
                
        # TODO Convert datetimes from strings to be able to use 
        for i in ["created", "milestone", "agreement", "PTO"]:
            if data[i].dtype == object:
                data[i] = pd.to_datetime(data[i], errors = "coerce")
        return data
    
    @staticmethod    
    def formatDate(x):
        if x is not pd.NaT:
            return x.strftime("%m-%d-%Y")
        else:
            return None
    
    @staticmethod
    def formatDatetime(x):
        if x is not pd.NaT:
            return x.strftime("%m-%d-%Y %I%p")
        else:
            return None
        
    
    @staticmethod
    def stripDatetime(x):
        try:
            return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        except:
            return None
        
    @staticmethod
    def stripDate(x):
        # try:
        if x:
            print(x)
            print(type(x))
            return datetime.datetime.strptime(x, "%Y-%m-%d").date()
        else:
            return None
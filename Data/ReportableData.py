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
        # except:
        #     return None
    
    # @staticmethod
    # def stripDate(x):
    #     datetime = self.stripDatetime(x)
    #     return datetime if datetime else None
            
        
#         self.leads = raw_data

        
#         if self.leads.empty:
#             message = "{} has no leads".format(self.name)
#             logging.debug(message)
#             raise ValueError(message)
        
#         self._source = self._groupedOutput("lead_source")
#         self._status = self._groupedOutput("lead_status")
        
#         # self.closers = self.leads["owner"].unique()
#         # self.leads["setter"] = self.leads["setter"].apply(self.removeCloserAsSetter)
#         # self.setters = self.leads["setter"].unique()
        
#         # if "Enerflo Admin" in self.closers:
#         #     self.leads = self.leads[self.leads["owner"] != "Enerflo Admin"]
        
#         # leads = self.leads.copy()
#         # leads["setter"] = leads["setter"].replace("Austin Anderson- Call Center", "Austin Anderson")
#         # self.leads = leads
        
#         # self.leads["dashboard"] = self.leads.apply(self._createDashboard, axis = 1)

#         # if prepForReport:
#         #     self._reportPrep()
    
#     @staticmethod
#     def _createDashboard(x):
#         return "https://enerflo.io/customer/edit/{}".format(x.name)
    
#     def _reportPrep(self):
        
#         toDate = lambda x: x.strftime('%m-%d-%Y')
        
#         def toDatetime(x):
#             if x is not pd.NaT:
#                 stamp = x.strftime('%m-%d-%Y %I%p').split(" ")
#                 return " ".join([stamp[0], stamp[1].strip("0")])
#             else:
#                 None
        
#         self.leads["created"] = self.leads["created"].apply(toDate)
#         self.leads["nextApptDate"] = self.leads["nextApptDate"].apply(toDatetime)
        
#         value_changes = {"name": "No Name",
#                          "email": "No Email",
#                          "lead_source": "No Source",
#                          "lead_status": "No Dispo",
#                          "notes": "-",
#                          "nextApptDetail": "-",
#                          "setter": "No Setter",
#                          "owner": "No Closer",
#                          "nextApptDate": "-"}
        
#         leads = self.leads.copy()
        
#         for i in list(value_changes.keys()):
#             if i in leads.columns:
#                 leads[i].fillna(value_changes[i], inplace = True)
                
#         self.leads = leads

#     def _groupedOutput(self, column):
#         output = self.leads.groupby(column).count()["name"]
#         output.rename(self.name, inplace = True)
#         return output
    
#     # Requires a grouping as an input to be to return a total
#     @staticmethod
#     def _getGroupedTotal(value, group):
#         try:
#             return group.loc[value]
#         except:
#             # print("{} not found in grouping")
#             return 0        
        
#     # Handles potential ZeroDivisionErrors while running the rep
#     def _potentialDivisionError(self, num, denom, percentage = True):
        
#         try:
#             if percentage:
#                 # print("{} / {} = {}".format(num, denom, num/denom))
#                 return 100 * (num/denom)
#             else:
#                 return num/denom
#         except ZeroDivisionError:
#             logging.warning("Division Error Avoided on {}".format(self.name))
#             return 0
#         except:
#             raise ValueError("Non ZeroDivisionError occured")

#     # Takes out closers from setters
#     removeCloserAsSetter = lambda self, x: x if x not in self.closers else None        

#     # Only returns a number of pitched leads. See _getPitchedLeads for the DF with customer information
#     def _getPitched(self):
#         return self.numSigns + self._getGroupedTotal("Pitched", self._status) + self._getGroupedTotal("Signed- Canceled", self._status)

#     # Gets all sits, which includes multiple disposition categories
#     def _getPitchedLeads(self, source_leads):
#         everything = pd.DataFrame()
#         for i in ["Signed", "Signed- Canceled", "Pitched"]:
#             try:
#                 to_add = source_leads[source_leads["lead_status"] == i]
#                 everything = pd.concat([everything, to_add])
#             except AttributeError:
#                 print("No Attribute {}".format(i))
#         return everything
    
# class InstallData:
    
#     def __init__(self, name, data):
#         self.name = name
#         self.installs = data
    
    
           
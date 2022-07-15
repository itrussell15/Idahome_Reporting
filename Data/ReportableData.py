# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:02:01 2022

@author: Schmuck
"""

import datetime
import pandas as pd

class ReportableData:
    
    # TODO Focus on getting this into a good spot before trying to pull reports.
    # Decide when to turn nans into a string or static value. 

    def __init__(self, name, raw_data, prepForReport):
        self.name = name
        self.leads = raw_data
        
        if self.leads.empty:
            raise ValueError("{} has no leads".format(self.name))
        
        self._source = self._groupedOutput("lead_source")
        self._status = self._groupedOutput("lead_status")
        
        self.closers = self.leads["owner"].unique()
        self.leads["setter"] = self.leads["setter"].apply(self.removeCloserAsSetter)
        self.setters = self.leads["setter"].unique()
        
        if prepForReport:
            self._reportPrep()
            
    def _reportPrep(self):
        value_changes = {"name": "No Name",
                         "email": "No Email",
                         "lead_source": "No Source",
                         "lead_status": "No Dispo",
                         "notes": "-",
                         "nextApptDetail": "-",
                         "setter": "No Setter",
                         "owner": "No Closer"}
        
        for i in list(value_changes.keys()):
            if i in self.leads.columns:
                self.leads[i].fillna(value_changes[i], inplace = True)
            
        self.leads["setter"] = self.leads["setter"].replace("Austin Anderson- Call Center", "Austin Anderson")

    def _groupedOutput(self, column):
        output = self.leads.groupby(column).count()["name"]
        output.rename(self.name, inplace = True)
        return output
    
    # Requires a grouping as an input to be to return a total
    @staticmethod
    def _getGroupedTotal(value, group):
        try:
            return group.loc[value]
        except:
            # print("{} not found in grouping")
            return 0        
        
    # Handles potential ZeroDivisionErrors while running the rep
    @staticmethod
    def _potentialDivisionError(num, denom, percentage = True):
        
        try:
            if percentage:
                # print("{} / {} = {}".format(num, denom, num/denom))
                return 100 * (num/denom)
            else:
                return num/denom
        except ZeroDivisionError:
            return 0
        except:
            raise ValueError("Non ZeroDivisionError occured")

    # Takes out closers from setters
    removeCloserAsSetter = lambda self, x: x if x not in self.closers else None        

    # Only returns a number of pitched leads. See _getPitchedLeads for the DF with customer information
    def _getPitched(self):
        return self.numSigns + self._getGroupedTotal("Pitched", self._status) + self._getGroupedTotal("Signed- Canceled", self._status)

    # Gets all sits, which includes multiple disposition categories
    def _getPitchedLeads(self, source_leads):
        everything = pd.DataFrame()
        for i in ["Signed", "Signed- Canceled", "Pitched"]:
            try:
                to_add = source_leads[source_leads["lead_status"] == i]
                everything = pd.concat([everything, to_add])
            except AttributeError:
                print("No Attribute {}".format(i))
        return everything
           
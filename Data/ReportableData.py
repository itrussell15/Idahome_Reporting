# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:02:01 2022

@author: Schmuck
"""

import datetime
import pandas as pd

class ReportableData:

    def __init__(self, name, raw_data, previous_weeks = 6):
        self.name = name
        
        if previous_weeks:
            today = datetime.datetime.today()
            self.leads = raw_data[raw_data["Added"] >= today - datetime.timedelta(weeks = previous_weeks)]
        else:
            self.leads = raw_data
            
        self._source = self._groupedOutput("Lead Source")
        self._status = self._groupedOutput("Lead Status")
        
        # Can drop all the duplicates
        # self.duplicated = self.leads[self.leads.duplicated("Customer")]
        # self.leads = self.leads.drop_duplicates(subset = "Customer", keep = "first").copy()

    def _groupedOutput(self, column):
        output = self.leads.groupby(column).count()["ID"]
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
                return 100 * (num/denom)
            else:
                return num/denom
        except ZeroDivisionError:
            return 0
        except:
            raise ValueError("Non ZeroDivisionError occured")

    # Only returns a number of pitched leads. See _getPitchedLeads for the DF with customer information
    def _getPitched(self):
        return self.numSigns + self._getGroupedTotal("Pitched", self._status) + self._getGroupedTotal("Signed- Canceled", self._status)

    # Gets all sits, which includes multiple disposition categories
    def _getPitchedLeads(self, source_leads):
        everything = pd.DataFrame()
        for i in ["Signed", "Singed- Canceled", "Pitched"]:
            try:
                to_add = source_leads[source_leads["Lead Status"] == i]
                everything = pd.concat([everything, to_add])
            except AttributeError:
                print("No Attribute {}".format(i))
        return everything
           
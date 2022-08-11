#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 22:29:28 2022

@author: isaactrussell
"""

import datetime
import pandas as pd

class Installs:
    
    def __init__(self, name, data_obj):
        self.name = name
        self._data = data_obj.data
        
        self._filterData()
    
    def _filterData(self):
        self._data = self._data[~self._data["status"].isin(["Cancelled", "On Hold"])]
        self._data = self._data[(self._data["agreement"] >= self.start_date) | (self._data["PTO"] >= self.start_date)]
        self._data.rename(columns = {"agreement": "Agreement"}, inplace = True)
        # self._data["PTO"] = self._data["PTO"].apply(lambda x: x.date())
        
    def summaryData(self, column):
        df = self._data[self._data[column] >= self.start_date]
        headers = ["Deals", "kWs", "Cost"]
        values = [str(len(df)), "{:.2f} kWs".format(df["system_size"].sum()), self._moneyFormat(df["gross_cost"].sum())]
        return [headers, values]
    
    @staticmethod
    def _moneyFormat(x):
        return "${:0,.2f}".format(x)
    
    @staticmethod
    def _presentableDate(x):
        return x.strftime("%m-%d-%Y")
    
    def getInstalls(self, column): 
        table = self._data[self._data[column] >= self.start_date]
        pull_vals = ["customer", "closer", "system_size", "Agreement"]
        table = table[pull_vals]
        
        display_columns = ["Customer", "Closer", "System Size", "Agreement Date"]
        table.columns = display_columns
        table["Agreement Date"] = table["Agreement Date"].apply(self._presentableDate)
        return table
    
    @property
    def agreements(self):
        table = self.getInstalls("Agreement")
        return table
        
    @property
    def PTOs(self):
        table = self.getInstalls("PTO")
        table = pd.merge(table, self._data["PTO"], left_index = True, right_index = True)
        table["PTO"] = table["PTO"].apply(lambda x: x.date())
        table["PTO"] = table["PTO"].apply(self._presentableDate)
        return table
    
    @property
    def data(self):
        return self._data
    
    @property
    def start_date(self):
        today = datetime.date.today()
        return datetime.datetime(year = today.year, month = today.month, day = 1)
    
    @property
    def upcomingInstalls(self):
        return None
    
    @property
    def PTO_Table(self):
        table = self._summaryTable()
        return None
    
    @property
    def AgreementTable(self): 
        table = self._summaryTable()
        return None
    
if __name__ == "__main__":
    from DataHandler import DataHandler
    
    data = DataHandler(previous_weeks = 6)
    
    installs = Installs("Test", data.installs)
    # print(installs.data.head())
    print(installs.PTOs)
        
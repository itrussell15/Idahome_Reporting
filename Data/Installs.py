#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 22:29:28 2022

@author: isaactrussell
"""

import datetime

class Installs:
    
    def __init__(self, name, data_obj):
        self.name = name
        self._data = data_obj.data
        
        self._filterData()
         
    
    def _filterData(self):
        self._data = self._data[~self._data["status"].isin(["Cancelled", "On Hold"])]
        self._data = self._data[(self._data["agreement"] >= self.start_date) | (self._data["PTO"] >= self.start_date)]
    
    def summaryData(self, column):
        df = self._data[self._data[column] >= self.start_date]
        deals = ["Deals", str(len(df))]
        totalKws = ["kWs", "{:.2f} kWs".format(df["system_size"].sum())]
        totalCost = ["Cost", "${:.2f}".format(df["gross_cost"].sum())]
        return [deals, totalKws, totalCost]
    
    def getInstalls(self):
        table = self.data.dropna(subset = ["install_date"])
        return table.sort_values(by = "install_date", ascending = False)
    
    @property
    def agreements(self):
        return self._data[self._data["agreement"] >= self.start_date]
    
    @property
    def PTOs(self):
        return self._data[self._data["PTO"] >= self.start_date]
    
    @property
    def totalKw(self):
        return self.data["system_size"].sum()
    
    @property
    def numAgreements(self):
        return len(self.agreements)

    @property
    def totalCosts(self):
        return self.data["gross_cost"].sum()
    
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
    print(installs.summaryData("PTO"))
    print(installs.summaryData("agreement"))
    # print(installs.data.head())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 22:29:28 2022

@author: isaactrussell
"""

import datetime
import pandas as pd
import matplotlib.pyplot as plt

class Installs:
    
    def __init__(self, name, data_obj):
        self.name = name
        print(type(data_obj))
        if type(data_obj) != type(pd.DataFrame):
            # Importing DataFrame 
            self._data = data_obj
        else:
            # Normal use case
            self._data = data_obj.data
        
        self._filterData()
        
    def importDataFrame(self):
        # TODO Convert datetimes from strings to be able to use  
        pass
    
    def _filterData(self):
        self._original = self._data
        self._data = self._data[~self._data["status"].isin(["Cancelled", "On Hold"])]
        self._data = self._data[(self._data["agreement"] >= self.start_date) | (self._data["PTO"] >= self.start_date)]
        self._data.rename(columns = {"agreement": "Agreement"}, inplace = True)
        # self._data["PTO"] = self._data["PTO"].apply(lambda x: x.date())
    
    # TODO Create automatic payout column that will scale based on the number of PTOs and number of agreements and multiply by the number of kWs
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
    
    def performance(self, column):
        monthly = self.monthlys(column)
        plt.bar(monthly.index, monthly.total)
        plt.scatter(monthly.index, monthly.kWs, linestyle = "--")
        
    
    def monthlys(self, column):
        getMonth = lambda x: "{}-{}".format(x.month, x.year)
        group = self.original.groupby(pd.Grouper(key = column, freq = "M"))
        df = pd.DataFrame()
        df["total"] = group.count()["customer"]
        df["kWs"] = group.sum()["system_size"]
        df["cost"] = group.sum()["gross_cost"]
        df["month"] = df.index.map(getMonth)
        df.set_index("month", inplace = True)
        return df
    
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
    def original(self):
        return self._original
    
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
    # from DataHandler import DataHandler
    # data = DataHandler(previous_weeks = 6)
    import json
    with open("install_data.json", "r") as f:
        data = json.load(f)
    data = pd.DataFrame.from_dict(data)
    installs = Installs("Test", data)
    # # print(installs.data.head())
    # print(installs.performance("PTO"))
        
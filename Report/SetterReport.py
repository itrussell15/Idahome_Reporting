# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:25:22 2022

@author: Schmuck
"""

from ReportTemplate import Report
import pandas as pd
import numpy as np


class _SetterReport(Report):
    
    def __init__(self, title, data_handler = None, data_path = None):
        super().__init__(title = title,
                         report_type = "Setter",
                         handler = data_handler,
                         data_path = data_path)
        
    

class SetterIndividualReport(_SetterReport):
    
    def __init__(self, name, handler = None, path = None):
        super().__init__(name, data_handler=handler, data_path = path)
        setter = self._data.getSetterData(name)
        self._create_body(setter)
        
    def _create_body(self, setter):
        self._customerTable(setter)
        self.ln(10)
    
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38]}
        
        pull_values = ["Customer", "Lead Status"]
        customers = subject.leads[pull_values]
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Leads", cell_size)
        
class SetterOfficeReport(_SetterReport):
    
    def __init__(self, handler = None, path = None):
        super().__init__("Idahome Solar", data_handler = handler, data_path = path)
        office = self._data.getSetterData()
        self._create_body(office)
        
    def _create_body(self, setter):
        self._customerTable(setter)
        self.ln(10)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 25, 60]}
        
        pull_values = ["Customer", "Lead Status", "Setter"]
        customers = subject.leads[pull_values].astype(str)
        customers.sort_values(by = "Setter", ascending = True, inplace = True)
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Leads", cell_size)

if __name__ == "__main__":
    import os
    path = os.path.dirname(os.getcwd()) + "/Data/Data.xlsx"
    # report = SetterIndividualReport("Cole Newell", path = path)
    report = SetterOfficeReport(path = path)
    report.output()
    
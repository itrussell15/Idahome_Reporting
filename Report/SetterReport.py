# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:25:22 2022

@author: Schmuck
"""

import sys
sys.path.append("../Data")

from ReportTemplate import Report
import pandas as pd
import numpy as np


class _SetterReport(Report):
    
    def __init__(self, title, data_handler = None, data_path = None):
        super().__init__(title = title,
                         report_type = "Setter",
                         handler = data_handler,
                         data_path = data_path)
        
    def KPIs(self, subject):
        columns = ["Total Leads", "Lead-Pitched", "Lead-Signed",  "% No Show"]
        data = [subject.numLeads, subject.pitchRatio, subject.closeRatio,  subject.cancelRatio]
        data = ["{:.2f}%".format(i) for i in data]
        data[0] = str(subject.numLeads)
        final = [columns, data]
        
        cell_size = {"height": 6, "widths": [35, 35, 35, 35]}
        self._createTable(final, "KPIs", cell_size = cell_size)
    
class SetterIndividualReport(_SetterReport):
    
    def __init__(self, name, handler = None, path = None):
        super().__init__(name, data_handler=handler, data_path = path)
        setter = self._data.getSetterData(name)
        self._create_body(setter)
        
    def _create_body(self, setter):
        self.KPIs(setter)
        self.ln(10)
        self._customerTable(setter)

    
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
        
    def _create_body(self, office):
        self.KPIs(office)
        self.ln(10)
        self._customerTable(office)
        
        
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
    
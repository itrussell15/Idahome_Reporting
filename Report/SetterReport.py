# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:25:22 2022

@author: Schmuck
"""

import sys

from ReportTemplate import Report
import pandas as pd
import numpy as np
import logging

class _SetterReport(Report):
    
    def __init__(self, title, data_handler = None):
        super().__init__(title = title,
                         report_type = "Setter",
                         data_handler = data_handler)
        logging.info("Setter Report Creation initiated for {}".format(title))
        
    def KPIs(self, subject):
        table = subject.KPIs
        
        cell_size = {"height": 6, "widths": [35, 35, 35]}
        self._createTable(table, "KPIs", cell_size = cell_size)
    
class SetterIndividualReport(_SetterReport):
    
    def __init__(self, name, handler = None):
        super().__init__(name, data_handler = handler)
        setter = self._data.getSetter(name)
        self._create_body(setter)
        
    def _create_body(self, setter):
        self.KPIs(setter)
        self.ln(10)
        self._customerTable(setter)
     
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 25, 38]}
        table = subject.customerTable.copy()
        self._createTable(table, "Leads", cell_size)
        
class SetterOfficeReport(_SetterReport):
    
    def __init__(self, handler = None, path = None):
        super().__init__("Idahome Solar", data_handler = handler)
        office = self._data.getSetterData()
        self._create_body(office)
        
    def _create_body(self, office):
        self.KPIs(office)
        self.ln(10)
        self._customerTable(office)

    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [64, 27, 42, 25, 38]}
        self._createTable(subject.customerTable, "Leads", cell_size)

if __name__ == "__main__":

    # report = SetterOfficeReport()
    report = SetterIndividualReport("Kyle Wagner")
    report.output()
    
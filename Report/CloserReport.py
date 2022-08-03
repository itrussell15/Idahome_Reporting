# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:53:39 2022

@author: Schmuck
"""

import sys

from Report.ReportTemplate import Report
import pandas as pd
import numpy as np
import os
import logging

class _CloserReport(Report):
    
    def __init__(self, title, data_handler):
        super().__init__(title = title, report_type = "Closer", data_handler = data_handler)
        logging.info("Closer Report Creation initiated for {}".format(title))
    
    # Soon be deprecated
    def _create_KPI_table(self, subject):
        cell_size = {"height": 6, "widths": [45, 45, 45]}
        data = [["Pitched-Lead", "Signed-Pitched", "Pull Through"],
                ["{:.2f} %".format(subject.pitchRatio), "{:.2f} %".format(subject.closeRatio), "{:.2f} %".format(subject.pullThroughRatio)]]
        
        self._createTable(data, "KPIs", cell_size, cell_text_size = 12)

    def _createSourceMatrix(self, subject):
        cell_size = {"height": 6, "widths": [40, 20, 20, 20, 28, 28, 28]}
        
        headers = ["Source"]
        headers.extend(list(subject.finalTable.columns))
        temp = subject.finalTable.copy()
        for i in ["Pitched %", "Pitch-Signed", "Lead-Signed"]:
            temp[i] = temp[i].apply(lambda x: "{:.2f}".format(x))
        totals = []
        for i in ["Leads", "Pitched", "Signs"]:
            totals.append(temp[i].sum())
            temp[i] = temp[i].apply(lambda x: "{}".format(x))
        
        totals = [str(i) for i in totals]
        totals.extend("{:.2f}".format(i) for i in [subject.pitchRatio, subject.closeRatio, subject.closeRatioTotal])
        temp.loc["Totals"] = totals
        temp.reset_index(inplace = True)
        
        self._createTable(temp, "Sources", cell_size, bold_rows = [len(temp)])

class IndividualReport(_CloserReport):
    
    def __init__(self, closer_name, handler = None):
        super().__init__(closer_name, data_handler = handler)
        closer = self._data.getCloserData(closer_name)
        self.create_body(closer)    
        
    def create_body(self, closer):
        self._createSourceMatrix(closer)
        self.ln(10)
        self._customerTable(closer)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40]}
        
        pull_values = ["name", "lead_source", "lead_status"]
        customers = subject.leads[pull_values].fillna("Null")
        
        customers.columns = ["Customer", "Source", "Status"]
        
        self._createTable(customers, "Leads", cell_size)
        
class OfficeReport(_CloserReport):
    
    def __init__(self, handler = None):
        super().__init__("Idahome Solar", data_handler = handler)
        office = self._data.getCloserData()
        self.create_body(office)
        
    def create_body(self, office):
        self._createSourceMatrix(office)
        self.ln(10)
        self._LeadGenerationMatrix(office)
        self.add_page()
        self._LeadStatusMatrix(office)
        self.ln(10)
        self._customerTable(office)
        
    def _LeadGenerationMatrix(self, subject):
        # Get data as single numbers and into strings
        data = subject.closerLeadGeneration()
        for_totals = data.copy().sum().values
        data.loc["Totals"] = for_totals
        
        data = data.astype(int).astype(str)
        data.reset_index(inplace = True)
        data = data.rename(columns = {'index':'Closer',
                                      "Website/Called In": "Website",
                                      "Sales Rabbit": "Sales Rbt"})
        widths = [16 for _ in range(len(data.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        self._createTable(data, "Lead Source by Rep", cell_size, header_size=6, bold_rows = [len(data)])
        
    def _LeadStatusMatrix(self, subject):
        # Get data as single numbers and into strings
        data = subject.closerLeadStatus()
        for_totals = data.copy().sum().values
        data.loc["Totals"] = for_totals
        
        data = data.astype(int).astype(str) 
        data.loc["Percentages"] = ["{:.2f}%".format(100*i) for i in for_totals/sum(for_totals)]
        data.reset_index(inplace = True)
        data = data.rename(columns = {"index": "Closer", "Signed- Canceled": "Sign-Cncl"})
        widths = [20 for _ in range(len(data.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        
        self._createTable(data, "Lead Status by Rep", cell_size, header_size = 7, bold_rows = [len(data), len(data)-1])
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 30, 40]}
        
        pull_values = ["name", "lead_source", "lead_status", "owner"]
        customers = subject.leads[pull_values].fillna("Null")
        customers.sort_values(by = "owner", ascending = True, inplace = True)
        customers.replace(to_replace = "Signed- Canceled", value = "Sign-Cncl", inplace = True)
        
        customers.columns = ["Customer", "Source", "Status", "Owner"]
        links = [str(i) for i in subject.leads["dashboard"].values]
        links.insert(0, None)
        
        self._createTable(customers, "Leads", cell_size, column_links = links)
        
if __name__ == "__main__":
    
    # report = IndividualReport("Zach Trussell")
    report = OfficeReport()
    report.output()
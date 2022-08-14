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
import datetime

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
        table = subject.finalTable
        
        self._createTable(table, "Sources", cell_size, bold_rows = [len(table)])
        
    def header(self):
        super().header()
        self.cell(220, 10, "{} - {}".format(
            (datetime.datetime.today() - datetime.timedelta(weeks = self._data.previous_weeks)).strftime("%m/%d/%Y"), datetime.date.today().strftime("%m/%d/%Y")), align = "C")
        # Line break
        self.ln(18)

class IndividualReport(_CloserReport):
    
    def __init__(self, closer_name, handler = None):
        super().__init__(closer_name, data_handler = handler)
        closer = self._data.getCloser(closer_name)
        self._name = closer_name
        self.create_body(closer)    
        
    def create_body(self, closer):
        self._createSourceMatrix(closer)
        self.ln(10)
        self._customerTable(closer)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40]}
        table = subject.customerTable.copy()
        
        self._createTable(table, "Leads", cell_size)
        
    def output(self):
        super().output()
        logging.info('Closer Report Generated for {}'.format(self._name))
        
class OfficeReport(_CloserReport):
    
    def __init__(self, handler = None):
        super().__init__("Idahome Solar", data_handler = handler)
        office = self._data.getCloser()
        self.create_body(office)
        
    def create_body(self, office):
        self._SummaryTable(office)
        self.ln(10)
        self._createSourceMatrix(office)
        self.ln(10)
        self.add_page()
        self._LeadGenerationMatrix(office)
        self.ln(10)
        self._LeadStatusMatrix(office)
        self.add_page()
        self._customerTable(office)
        
    def _SummaryTable(self, subject):
        table = subject.summaryTable
        widths = [45, 20, 20, 20, 28, 28, 28]
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "Summary Table", cell_size, header_size = 8)
        
    def _LeadGenerationMatrix(self, subject):
        # Get data as single numbers and into strings
        table = subject.closerLeadGeneration
        widths = [16 for _ in range(len(table.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "Lead Source by Rep", cell_size, header_size = 6, bold_rows = [len(table)])
        
    def _LeadStatusMatrix(self, subject):
        # Get data as single numbers and into strings
        data = subject.closerLeadStatus
        widths = [20 for _ in range(len(data.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        self._createTable(data, "Lead Status by Rep", cell_size, header_size = 7, bold_rows = [len(data), len(data)-1])
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 30, 40]}
        
        self._createTable(subject.customerTable, "Leads", cell_size)
        
    def output(self):
        super().output()
        logging.info('Closer Office Report Generated')
        
if __name__ == "__main__":
    
    # report = IndividualReport("Darren Phillips")
    report = OfficeReport()
    report.output()
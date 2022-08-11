#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 17:55:15 2022

@author: isaactrussell
"""

from ReportTemplate import Report
import datetime
import logging

class InstallReport(Report):
    
    def __init__(self, name, data_obj = None):
        super().__init__("Idahome Solar", report_type = "Install", data_handler = data_obj)
    
    @property
    def start_date(self):
        today = datetime.date.today()
        return datetime.datetime(year = today.year, month = today.month, day = 1)
    
    def header(self):
        super().header()
        
        self.cell(220, 10, "{} - {}".format(
            (self.start_date).strftime("%m/%d/%Y"), datetime.date.today().strftime("%m/%d/%Y")), align = "C")
        # Line break
        self.ln(18)
        
    def create_body(self, subject):
        self._PTO_Table(subject)
        self.ln(10)
        self._AgreementTable(subject)
        
    def _PTO_Table(self, subject):
        table = subject.summaryData("PTO")
        cell_size = {"height": 6, "widths": [30, 30]}
        self._createTable(table, "PTO Summary", cell_size)
    
    def _AgreementTable(self, subject):
        table = subject.summaryData("agreement")
        cell_size = {"height": 6, "widths": [30, 30]}
        self._createTable(table, "Agreement Summary", cell_size)
    
    def output(self):
        super().output()
        logging.info("Install Report Generated")
        
class OfficeReport(InstallReport):
    
    def __init__(self, data_obj = None):
        super().__init__("Idahome Solar", data_obj = data_obj)
        installs = self._data.getInstalls()
        self.create_body(installs)
        
if __name__ == "__main__":
    
    report = OfficeReport()
    report.output()
    
    
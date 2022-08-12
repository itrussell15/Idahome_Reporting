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
    
    def __init__(self, name, handler = None):
        super().__init__("Idahome Solar", report_type = "Install", data_handler = handler)
    
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
        self.summaryTable("PTO", subject)
        self.ln(10)
        self.summaryTable("Agreement", subject)
        self.ln(10)
        self.PTO_Table(subject)
        self.ln(10)
        self.agreementTable(subject)
    
    def summaryTable(self, column, subject):
        table = subject.summaryData(column)
        widths = [40 for _ in range(len(table[0]))]
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "{} Summary".format(column), cell_size, header_size = 9)
        
    def agreementTable(self, subject):
        table = subject.agreements
        widths = [35 for _ in range(len(table.columns))]
        widths[0] = 50
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "Agreements", cell_size)
        
    def PTO_Table(self, subject):
        table = subject.PTOs
        widths = [30 for _ in range(len(table.columns))]
        widths[0] = 65
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "PTOs", cell_size)
    
    def output(self):
        super().output()
        logging.info("Install Report Generated")
        
class OfficeReport(InstallReport):
    
    def __init__(self, handler = None):
        super().__init__("Idahome Solar", handler = handler)
        installs = self._data.getInstalls()
        self.create_body(installs)
        
if __name__ == "__main__":
    
    report = OfficeReport()
    report.output()
    
    
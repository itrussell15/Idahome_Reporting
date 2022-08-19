#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 17:55:15 2022

@author: isaactrussell
"""

import os
from ReportTemplate import Report
import datetime
import logging
import time

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
        self.summaryTable("Agreement", subject)
        self.ln(10)
        self.agreementTable(subject)
        self.add_page()
        self.summaryTable("PTO", subject)
        self.ln(10)
        self.PTO_Table(subject)
        self.add_page()
        
        self.performance("Agreement", subject)
        self.ln(1)
        self.performance("PTO", subject)
        self.ln(10)
        
    
    def performance(self, column, subject):
        subject.performance(column)
        image_w = int(self.WIDTH * 0.8)
        x = int((self.WIDTH - image_w)/2)
        self.set_font(self._font, 'B', 15)
        # self.cell(0, h = 10, txt = "{} Yearly Performance".format(column), align = 'C')
        # self.ln(9)
        self.image(os.getcwd() + "/assets/temp/{}_performance.png".format(column), x = x, w = image_w, h = 100)
    
    def summaryTable(self, column, subject):
        table = subject.summaryData(column)
        widths = [40 for _ in range(len(table[0]))]
        cell_size = {"height": 6, "widths": widths}
        self._createTable(table, "{} Summary".format(column), cell_size, header_size = 9)
        # self.ln(8)
        # self.performance(column, subject)
        
        
    def agreementTable(self, subject):
        table = subject.agreements
        widths = [35 for _ in range(len(table.columns))]
        widths[0] = 60
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
    from DataHandler import DataHandler
    import pandas as pd
    data = DataHandler(previous_weeks = 1)
    
    # import json
    # path = os.path.dirname(os.getcwd()) + "/Data/install_data.json"
    # with open(path, "r") as f:
    #     installs = json.load(f)
    # df = pd.DataFrame.from_dict(installs)

    # data.attachInstalls(df)
    
    report = OfficeReport(data)
    report.output()

    
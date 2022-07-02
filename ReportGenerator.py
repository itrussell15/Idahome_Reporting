# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 00:07:17 2022

@author: Schmuck
"""

from fpdf import FPDF
from DataHandler import DataHandler
import datetime, os
import numpy as np
import pandas as pd
from global_functions import *
import logging

class CloserReport(FPDF):
    
    def __init__(self, title, handler, data_path, fig_path = "/assets/temp"):
        super().__init__()
        if not data_path and not handler:
            raise ValueError("Either data_path or handler should be passed in")
        self.WIDTH = 210
        self.HEIGHT = 297
        self._title = title
        self._font = "Courier"
        self._fig_path = resource_path(fig_path)
        self._epw = self.w - self.l_margin
        
        if handler:
            self._data = handler
        else:
            self._data = DataHandler(data_path)
        self._cleanFigureFolder(fig_path)
        
        self.add_page()
        
    def header(self):
        self.image(resource_path("assets/logo.png"), 10, 8, 33)
        self.ln(10)
        # Arial bold 15
        self.set_font(self._font, 'B', 30)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(60, 10, "{} Report".format(self._title), align = "C")
        self.ln(11)
        self.set_font(self._font, 'B', 15)
        self.cell(220, 10, "{} - {}".format(
            (datetime.datetime.today() - datetime.timedelta(weeks = 6)).strftime("%m/%d/%Y"), datetime.date.today().strftime("%m/%d/%Y")), align = "C")
        # Line break
        self.ln(18)
        
    def footer(self):
        thisTime = datetime.datetime.now()
        self.set_font(self._font, "I", 10)
        self.set_y(-10)
        self.cell(0,10, "Report Generated at {}".format(thisTime.strftime("%m/%d/%Y, %H:%M:%S")), align = "C")
        self.set_x(-self.l_margin-5)
        self.cell(10, h = 8, txt = "Page {}".format(self.page_no()), align = "R")
        
    def output(self):
        thisTime = datetime.datetime.now()     
        self.out_path = resource_path("output/{}_Report_{}.pdf".format(self._title, thisTime.strftime("%m-%d-%Y")))
        super().output(self.out_path, "F")
        
    def _cleanFigureFolder(self, path):
        path = os.getcwd() + path
        for file in os.listdir(path):
            os.remove(path + "/" + file)
            
    def _createTable(self, data, title, cell_size, title_size = 15, cell_text_size = 9, header_size = 9):
        self.set_font(self._font, 'B', 15)
        self.cell(0, h = 10, txt = title, align = 'C')
        self.ln(10)
        columns = len(data[0])
        # to_center = round((self.WIDTH  - (columns * cell_size[0]))/2)
        to_center = round((self.WIDTH - sum([i for i in cell_size["widths"]]))/2)
        self.x = to_center
        
        for n, row in enumerate(data):
            
            self.x = to_center
            if n == 0:
                self.set_font(self._font, 'B', size = header_size)
                self.y = self.y + (cell_size["height"] * n)
            else:
                self.set_font(self._font, size = cell_text_size)
                self.y += cell_size["height"]
            if self.y > self.HEIGHT - self.b_margin - self.t_margin:
                self.add_page()
                self.y = self.t_margin + 35
                self.x = to_center
            # Cells in row
            for o, (value, width) in enumerate(zip(row, cell_size["widths"])):
                top = self.y
                self.multi_cell(width, cell_size["height"], value, border = 1, align = "C")
                self.x = sum([i for i in cell_size["widths"][:o + 1]]) + to_center
                self.y = top
                
    def _create_KPI_table(self, subject):
        cell_size = {"height": 6, "widths": [45, 45, 45]}
        data = [["Pitched-Lead", "Signed-Pitched", "Pull Through"],
                ["{:.2f} %".format(subject.pitchRatio), "{:.2f} %".format(subject.closeRatio), "{:.2f} %".format(subject.pullThroughRatio)]]
        
        self._createTable(data, "KPIs", cell_size, cell_text_size = 12)

    def _createSourceMatrix(self, subject):
        cell_size = {"height": 6, "widths": [40, 20, 20, 20, 30, 30]}
        
        headers = ["Source"]
        headers.extend(list(subject.finalTable.columns))
        temp = subject.finalTable.copy()
        for i in ["Pitched %", "Pitch-Signed", "Lead-Signed"]:
            temp[i] = temp[i].apply(lambda x: "{:.2f}".format(x))
        for i in ["Leads", "Signs", "Pitched"]:
            temp[i] = temp[i].apply(lambda x: "{}".format(x))
        temp.reset_index(inplace = True)
        
        bulk = pd.DataFrame(np.vstack([temp.columns, temp]))
        self._createTable(bulk.values, "Sources", cell_size)

    def create_body(self, subject, include_owner = False):        
        height = 6
        # data = [["Pitched-Lead", "Signed-Pitched", "Pull Through"],
        #         ["{:.2f} %".format(subject.pitchRatio), "{:.2f} %".format(subject.closeRatio), "{:.2f} %".format(subject.pullThroughRatio)]]
        
        # cell_size = {"height": height, "widths": [45, 45, 45]}
        # self._createTable(data, "KPIs", cell_size, cell_text_size = 12)
        
        self.ln(10)
        
        headers = ["Source"]
        headers.extend(list(subject.finalTable.columns))
        temp = subject.finalTable.copy()
        for i in ["Pitched %", "Pitch-Signed", "Lead-Signed"]:
            temp[i] = temp[i].apply(lambda x: "{:.2f}".format(x))
        for i in ["Leads", "Signs", "Pitched"]:
            temp[i] = temp[i].apply(lambda x: "{}".format(x))
        temp.reset_index(inplace = True)
        bulk = pd.DataFrame(np.vstack([temp.columns, temp]))
        cell_size = {"height": height, "widths": [40, 20, 20, 20, 30, 30]}
        self._createTable(bulk.values, "Sources", cell_size)
        
        self.ln(10) 
        
        if include_owner:
            pull_values = ["Customer", "Lead Source", "Lead Status", "Lead Owner"]
            cell_size = {"height": height, "widths": [65, 38, 40, 40]}
            customers = subject.leads[pull_values].fillna("Null")
            customers.sort_values(by = "Lead Owner", ascending = True, inplace = True)
            customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        else:
            pull_values = ["Customer", "Lead Source", "Lead Status"]
            cell_size = {"height": height, "widths": [65, 38, 40]}
            customers = subject.leads[pull_values].fillna("Null")
            customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Customers", cell_size)
        
class IndividualReport(CloserReport):
    
    def __init__(self, closer_name, handler = None, path = None):
        super().__init__(closer_name, handler, path)
        closer = self._data.getCloserData(closer_name)
        self.create_body(closer)    
        
    def create_body(self, closer):
        self._create_KPI_table(closer)
        self.ln(10)
        self._createSourceMatrix(closer)
        self.ln(10)
        self._customerTable(closer)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40]}
        
        pull_values = ["Customer", "Lead Source", "Lead Status"]
        customers = subject.leads[pull_values].fillna("Null")
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Customers", cell_size)
    
        
class OfficeReport(CloserReport):
    
    def __init__(self, path = None, handler = None):
        super().__init__("Office", handler = handler, data_path = path)
        office = self._data.getOfficeData()
        self.create_body(office)
        
    def create_body(self, office):
        self._create_KPI_table(office)
        self.ln(12)
        self._createSourceMatrix(office)
        self.ln(10)
        self._LeadGenerationMatrix(office)
        self.ln(10)
        
        self.add_page()
        self._customerTable(office)
        
    def _LeadGenerationMatrix(self, subject):
        # Get data as single numbers and into strings
        data = subject.closerLeadGeneration().astype(int).astype(str)
        
        # Bring Last 6 weeks to the left
        cols = data.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        data = data[cols]
        
        data.reset_index(inplace = True)
        data = data.rename(columns = {'index':'Closer', "Website/Called In": "Website"})
        widths = [18 for _ in range(len(data))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        data = pd.DataFrame(np.vstack([data.columns, data])).values
        
        self._createTable(data, "Lead Generation Matrix", cell_size, header_size=5)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40, 40]}
        
        pull_values = ["Customer", "Lead Source", "Lead Status", "Lead Owner"]
        customers = subject.leads[pull_values].fillna("Null")
        customers.sort_values(by = "Lead Owner", ascending = True, inplace = True)
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Customers", cell_size)

if __name__ == "__main__":
    path = "Data/Data.xlsx"
    report = OfficeReport(path = path)
    # report = IndividualReport("Zach Trussell", path = path)
    report.output()
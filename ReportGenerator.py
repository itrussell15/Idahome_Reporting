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

# %% Base Report Template
class Report(FPDF):
    
    def __init__(self, title, report_type, handler, data_path, fig_path = "/assets/temp"):
        super().__init__()
        if not data_path and not handler:
            raise ValueError("Either data_path or handler should be passed in")
        self.WIDTH = 210
        self.HEIGHT = 297
        self._report_type = report_type
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
        self.cell(60, 10, "{} Report".format(self._report_type), align = "C")
        self.ln(9)
        # Sub Title
        self.set_font(self._font, 'I', 18)
        self.cell(80)
        self.cell(60, 10, "{}".format(self._title), align = "C")
        self.ln(8)
        # Date Range
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
        path = resource_base() + "/" + path
        for file in os.listdir(path):
            os.remove(path + "/" + file)
            
    def _createTable(self, 
                     data, 
                     title, 
                     cell_size, 
                     title_size = 15, 
                     cell_text_size = 9,
                     header_size = 9,
                     bold_rows = []
                     ):
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
            elif n in bold_rows:
                self.set_font(self._font, "B", size = cell_text_size)
                self.y += cell_size["height"]
            else:
                self.set_font(self._font, size = cell_text_size)
                self.y += cell_size["height"]
                
            if self.y > self.HEIGHT - self.b_margin - self.t_margin:
                self.add_page()
                self.y = self.t_margin + 40
                self.x = to_center
            # Cells in row
            for o, (value, width) in enumerate(zip(row, cell_size["widths"])):
                top = self.y
                self.multi_cell(width, cell_size["height"], value, border = 1, align = "C")
                self.x = sum([i for i in cell_size["widths"][:o + 1]]) + to_center
                self.y = top
    
# %% Closer Report
class _CloserReport(_Report):
    
    def __init__(self, title, data_handler = None, data_path = None):
        super().__init__(title = title,
                         report_type = "Closer",
                         handler = data_handler,
                         data_path = data_path)
    
    # Soon be deprecated
    def _create_KPI_table(self, subject):
        cell_size = {"height": 6, "widths": [45, 45, 45]}
        data = [["Pitched-Lead", "Signed-Pitched", "Pull Through"],
                ["{:.2f} %".format(subject.pitchRatio), "{:.2f} %".format(subject.closeRatio), "{:.2f} %".format(subject.pullThroughRatio)]]
        
        self._createTable(data, "KPIs", cell_size, cell_text_size = 12)

    # Migrate this to DataHandler
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
        totals.extend(["-", "-", "-"])
        temp.loc["Totals"] = totals
            
        temp.reset_index(inplace = True)
        
        bulk = pd.DataFrame(np.vstack([temp.columns, temp]))
        self._createTable(bulk.values, "Sources", cell_size, bold_rows = [len(temp)])

class IndividualReport(_CloserReport):
    
    def __init__(self, closer_name, handler = None, path = None):
        super().__init__(closer_name, data_handler = handler, data_path = path)
        closer = self._data.getCloserData(closer_name)
        self.create_body(closer)    
        
    def create_body(self, closer):
        self._createSourceMatrix(closer)
        self.ln(10)
        self._customerTable(closer)
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40]}
        
        pull_values = ["Customer", "Lead Source", "Lead Status"]
        customers = subject.leads[pull_values].fillna("Null")
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Leads", cell_size)
        
class OfficeReport(_CloserReport):
    
    def __init__(self, path = None, handler = None):
        super().__init__("Idahome Solar", data_handler = handler, data_path = path)
        office = self._data.getCloserData()
        self.create_body(office)
        
    def create_body(self, office):
        # self._create_KPI_table(office)
        # self.ln(12)
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
                                      "No Lead Source": "No Source", 
                                      "Sales Rabbit": "Sales Rbt"})
        widths = [16 for _ in range(len(data.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        data = pd.DataFrame(np.vstack([data.columns, data])).values
        
        self._createTable(data, "Lead Source by Rep", cell_size, header_size=6, bold_rows = [len(data)-1])
        
    def _LeadStatusMatrix(self, subject):
        # Get data as single numbers and into strings
        data = subject.closerLeadStatus()
        for_totals = data.copy().sum().values
        data.loc["Totals"] = for_totals
        
        data = data.astype(int).astype(str) 
        data.loc["Percentages"] = ["{:.2f}%".format(100*i) for i in for_totals/sum(for_totals)]
        data.reset_index(inplace = True)
        data = data.rename(columns = {"index": "Closer"})
        widths = [20 for _ in range(len(data.columns))]
        widths[0] = 35
        cell_size = {"height": 6, "widths": widths}
        data = pd.DataFrame(np.vstack([data.columns, data])).values
        
        self._createTable(data, "Lead Status by Rep", cell_size, header_size = 5, bold_rows = [len(data)-1, len(data)-2])
        
    def _customerTable(self, subject):
        cell_size = {"height": 6, "widths": [65, 38, 40, 40]}
        
        pull_values = ["Customer", "Lead Source", "Lead Status", "Lead Owner"]
        customers = subject.leads[pull_values].fillna("Null")
        customers.sort_values(by = "Lead Owner", ascending = True, inplace = True)
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        self._createTable(customers, "Leads", cell_size)


# %% Main 
if __name__ == "__main__":
    path = "Data/Data.xlsx"
    # report = OfficeReport(path = path)
    report = IndividualReport("Cole Newell", path = path)
    report.output()
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

class Report(FPDF):
    
    def __init__(self, title, handler, data_path, fig_path = "/assets/temp"):
        super().__init__()
        if not data_path and not handler:
            raise ValueError("Either data_path or handler should be passed in")
        self.WIDTH = 210
        self.HEIGHT = 297
        self._title = title
        self._font = "Courier"
        self._fig_path = fig_path 
        self._epw = self.w - self.l_margin
        
        
        if handler:
            self._data = handler
        else:
            self._data = DataHandler(data_path)
        self._cleanFigureFolder(fig_path)
        
        self.add_page()
        
    def header(self):
        self.image("assets/logo.png", 10, 8, 33)
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
        self.out_path = "output/{}_Report_{}.pdf".format(self._title, thisTime.strftime("%m-%d-%Y"))
        super().output(self.out_path, "F")
        
    def _cleanFigureFolder(self, path):
        path = os.getcwd() + path
        for file in os.listdir(path):
            os.remove(path + "/" + file)

    def create_body(self, subject):
        
        def create_table(self, data, title, cell_size, title_size = 15, cell_sizes = 9):
            self.set_font(self._font, 'B', 15)
            self.cell(0, h = 10, txt = title, align = 'C')
            self.ln(10)
            
            columns = len(data[0])
            to_center = round((self.WIDTH  - (columns * cell_size[0]))/2)
            self.x = to_center
            
            for n, row in enumerate(data):
                
                # self.y = cell_size[1] * n
                self.x = to_center
                if n == 0:
                    self.set_font(self._font, 'B', size = cell_sizes)
                    self.y = self.y + (cell_size[1] * n)
                else:
                    self.set_font(self._font, size = cell_sizes)
                    self.y += cell_size[1]
                if self.y > self.HEIGHT - self.b_margin - self.t_margin:
                    self.add_page()
                    self.y = self.t_margin + 35
                    self.x = to_center
                    # break
                # Cells in row
                for o, value in enumerate(row):
                    top = self.y 
                    # if 
                    self.multi_cell(cell_size[0], cell_size[1], value, border =  1, align = "C")
                    self.x = ((o + 1) * cell_size[0]) + to_center
                    self.y = top
            
        data = [["Pitched-Lead", "Signed-Pitched", "Pull Through"],
                ["{:.2f} %".format(subject.pitchRatio), "{:.2f} %".format(subject.closeRatio), "{:.2f} %".format(subject.pullThroughRatio)]]
        cell_size = (40, 6)
        create_table(self, data, "KPIs", cell_size)
        
        self.ln(12)
        
        data = []
        headers = ["Source"]
        headers.extend(list(subject.finalTable.columns))
        # print(subject.finalTable)
        temp = subject.finalTable.copy()
        # print(temp)
        for i in ["Pitched %", "Pitch-Signed", "Lead-Signed"]:
            temp[i] = temp[i].apply(lambda x: "{:.2f}".format(x))
        for i in ["Leads", "Signs", "Pitched"]:
            temp[i] = temp[i].apply(lambda x: "{}".format(x))
        # bulk.reset_index(inplace = True)
        temp.reset_index(inplace = True)
        bulk = pd.DataFrame(np.vstack([temp.columns, temp]))
        # print(bulk.values)
        # bulk = [["{}".format(j) for j in i[1].values] for i in temp.iterrows()]
        # bulk.insert(0, headers)
        
        create_table(self, bulk.values, "Sources", (27, 6))
        
        self.ln(10)
        pull_values = ["Customer", "Lead Source", "Lead Status"]
        customers = subject.leads[pull_values].fillna("Null")
        customers = pd.DataFrame(np.vstack([customers.columns, customers])).values
        create_table(self, customers, "Customers", (55, 5))
        
class CloserReport(Report):
    
    def __init__(self, closer_name, handler = None, path = None):
        super().__init__(closer_name, handler, path)
        closer = self._data.getCloserData(closer_name)
        self.create_body(closer)    
        
class OfficeReport(Report):
    
        def __init__(self, path = None, handler = None):
            super().__init__("Office", handler = handler, data_path = path)
            office = self._data.getAllData()
            self.create_body(office)

if __name__ == "__main__":
    path = os.getcwd() + "/Data/Data.xlsx"
    # report = OfficeReport(path = path)
    report = CloserReport("Zach Trussell", path = path)
    report.output()
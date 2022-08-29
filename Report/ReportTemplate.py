# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 00:07:17 2022

@author: Schmuck
"""

import sys
# sys.path.append("..")

from DataHandler import DataHandler
from global_functions import resource_path, resource_base

from fpdf import FPDF
import datetime, os
import pandas as pd
import numpy as np

class Report(FPDF):
    
    def __init__(self, title, report_type, data_handler, fig_path = "/assets/temp"):
        super().__init__()
        
        # print(os.path.dirname(os.getcwd()))
        # self.add_font('Arial', "", fname = resource_path(os.getcwd() + "/assets/arial.ttf"))
        # self.set_doc_option("core_fonts_encoding", "windows-1252")
        
        self.WIDTH = 210
        self.HEIGHT = 297
        self._report_type = report_type
        self._title = title
        self._font = "Courier"
        self._fig_path = resource_path(fig_path)
        self._epw = self.w - self.l_margin
        
        if data_handler:
            self._data = data_handler
        else:
            self._data = DataHandler()
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
        
    def footer(self):
        thisTime = datetime.datetime.now()
        self.set_font(self._font, "I", 10)
        self.set_y(-10)
        self.cell(0,10, "Report Generated at {}".format(thisTime.strftime("%m/%d/%Y, %H:%M:%S")), align = "C")
        self.set_x(-self.l_margin-5)
        self.cell(10, h = 8, txt = "Page {}".format(self.page_no()), align = "R")
        
    # Add ability to seperate into different folders.
    # ie have a setter and a closer folder
    # IDEA to have office reports in output folder and then closers and setters in folders
    def output(self, folder = None):
        thisTime = datetime.datetime.now()  
        if not folder:
            self.out_path = resource_path("output/{}_{} Report_{}.pdf".format(self._title, self._report_type, thisTime.strftime("%m-%d-%Y")))
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
                     bold_rows = [],
                     column_links = None
                     ):
        if type(data) == pd.DataFrame:
            data = data.fillna("Null").copy().astype(str)
            data = pd.DataFrame(np.vstack([data.columns, data])).values
        self.set_font(self._font, 'B', 15)
        self.cell(0, h = 10, txt = title, align = 'C')
        self.ln(10)
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
                # import time
                # time.sleep(0.1)
                # print(value)
                self.cell(width, cell_size["height"], str(value).encode('utf-8').decode('latin-1'), border = 1, align = "C")
                self.x = sum([i for i in cell_size["widths"][:o + 1]]) + to_center
                self.y = top

if __name__ == "__main__":
    path = "Data/Data.xlsx"
    # report = OfficeReport(path = path)
    # report = IndividualReport("Cole Newell", path = path)
    # report.output()
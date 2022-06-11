# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 00:07:17 2022

@author: Schmuck
"""

from fpdf import FPDF
from DataHandler import DataHandler
import datetime, os

class Report(FPDF):
    
    def __init__(self, type_, title, path):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self._title = title
        self._font = "Courier"
        self._type = type_
        self._data = DataHandler(path)
        
    def header(self):
        self.image("assets/logo.png", 10, 8, 33)
        self.ln(10)
        # Arial bold 15
        self.set_font(self._font, 'B', 30)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(60, 10, "{} Report".format(self._type), align = "C")
        self.ln(11)
        self.set_font(self._font, 'B', 15)
        self.cell(10+80+130, 10, self._title, align = "C")
        # Line break
        self.ln(20)
        
    def footer(self):
        thisTime = datetime.datetime.now()
        self.set_font(self._font, "I", 10)
        self.set_y(-10)
        self.cell(self.WIDTH,10, "Report Generated at {}".format(thisTime.strftime("%m/%d/%Y, %H:%M:%S")), align = "C")
        
    def output(self):
        thisTime = datetime.datetime.now()
        super().output("output/{}_{}_Report_{}.pdf".format(self._title, self._type, thisTime.strftime("%m-%d-%Y"), "F"))
        
class CloserReport(Report):
    
    def __init__(self, closer_name, path):
        super().__init__("Closer", closer_name, path)
        
        
class OfficeReport(Report):
    
    def __init__(self, office, path):
        super().__init__("Office", office, path)
        
class AllReport(Report):
    
        def __init__(self, path):
            super().__init__("All", "", path)

if __name__ == "__main__":
    path = os.getcwd() + "/Data/Data.xlsx"
    report = CloserReport("Vin Santangelo", path)
    # report = OfficeReport("Idahome Electric", path)
    report.add_page()
    report.output()
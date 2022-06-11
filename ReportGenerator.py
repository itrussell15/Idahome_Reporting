# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 00:07:17 2022

@author: Schmuck
"""

from fpdf import FPDF
import datetime

class Report(FPDF):
    
    def __init__(self, title):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self._title = title
        self._font = "Courier"
        
    def header(self):
        self.image("assets/logo.png", 10, 8, 33)
        self.ln(10)
        # Arial bold 15
        self.set_font(self._font, 'B', 30)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(60, 10, "Closer Report", align = "C")
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
        
class CloserReport(Report):
    
    def __init__(self, closer_name):
        super().__init__(closer_name)
        
class OfficeReport(Report):
    
    def __init__(self):
        super().__init__("Office Report")
        

if __name__ == "__main__":
    report = CloserReport("Vin Santangelo")
    # report = OfficeReport()
    report.add_page()
    report.output("test1.pdf", "F")
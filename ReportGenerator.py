# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 00:07:17 2022

@author: Schmuck
"""

from fpdf import FPDF
from DataHandler import DataHandler
import datetime, os

class Report(FPDF):
    
    def __init__(self, type_, title, handler, data_path, fig_path = "/assets/temp"):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        self._title = title
        self._font = "Courier"
        self._type = type_
        self._fig_path = fig_path 
        
        if handler:
            self._data = handler
        else:
            self._data = DataHandler(data_path)
        self._cleanFigureFolder(fig_path)
        
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
        self.ln(12)
        
    def footer(self):
        thisTime = datetime.datetime.now()
        self.set_font(self._font, "I", 10)
        self.set_y(-10)
        self.cell(0,10, "Report Generated at {}".format(thisTime.strftime("%m/%d/%Y, %H:%M:%S")), align = "C")
        
    def output(self):
        thisTime = datetime.datetime.now()       
        super().output("output/{}_{}_Report_{}.pdf".format(self._title, self._type, thisTime.strftime("%m-%d-%Y"), "F"))
        
    def _cleanFigureFolder(self, path):
        path = os.getcwd() + path
        for file in os.listdir(path):
            os.remove(path + "/" + file)
            
    # def GenerateGraphs(self, graphFunctions):
    #     for img in graphFunctions.values():
    #         img(percentages = True, color = "orange", save_image = True, path = self._fig_path)
        
class CloserReport(Report):
    
    def __init__(self, closer_name, handler = None, path = None):
        super().__init__("Closer", closer_name, handler, path)
        self.add_page()
        closer = self._data.getCloserData(closer_name)
        self.create_body(closer.numSigns,
                         closer.numLeads,
                         closer.closeRatio,
                         {"Dispositions": closer.graphDisposition, "Lead Generation": closer.graphGeneration})
        self.output()
        
    def create_body(self, signs, leads, ratio, graphFunctions):
        self.set_font(self._font, 'B', 12)        
        self.cell(0, 15, "{} Signs | {} Leads | {:.2f}% Conversion".format(signs, leads, ratio), align = "C")
        y_i = 75
        steps = 110
        self.ln(20)
        self.set_font(self._font, 'B', 15)
        for i in graphFunctions.items():
            
            i[1](i[0], percentages = True, color = "orange", save_image = True, path = self._fig_path )
            # print(os.getcwd() + self._fig_path + "/{}.png".format(i[0]))
            self.image(os.getcwd() + self._fig_path + "/{}.png".format(i[0]),
                        7,
                        y_i, 
                        self.WIDTH)
            self.cell(0, 12, i[0], align = "C")
            y_i += steps - 5
            self.ln(steps)        
        
class OfficeReport(Report):
    
    def __init__(self, office, handler = None, path = None):
        super().__init__("Office", office, handler, path)
        
class AllReport(Report):
    
        def __init__(self, path):
            super().__init__("All", "", path)

if __name__ == "__main__":
    path = os.getcwd() + "/Data/Data.xlsx"
    # report = CloserReport("Josh Hodges", path = path)
    report = OfficeReport("Idahome Electric", handler = None, path = path)
    # report.output()
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

from ReportGenerator import IndividualReport, OfficeReport
from DataHandler import DataHandler

data = DataHandler("Data/Data.xlsx")

office_report = OfficeReport(handler = data)
office_report.output()
print("Created Office Report")

for i in data.closers:
    try:
        if i not in ["Enerflo Admin", "No Owner"]:
            report = IndividualReport(i, handler = data)
            report.output()
            print("Created Report for {}".format(i))
    except:
        pass
        # print("**ERROR on {}***".format(i))
        
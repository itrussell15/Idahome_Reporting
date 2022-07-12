# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

import sys

sys.path.append("Data")
sys.path.append("")

from Report.CloserReport import IndividualReport, OfficeReport
from Report.SetterReport import SetterIndividualReport, SetterOfficeReport
from Data.DataHandler import DataHandler

data = DataHandler("Data/Data.xlsx")

office_report = OfficeReport(handler = data)
office_report.output()
print("Created Closer Office Report")

for i in data.closers:
    try:
        if i not in ["Enerflo Admin", "No Owner"]:
            report = IndividualReport(i, handler = data)
            report.output()
            print("Closer Report Created for {}".format(i))
    except Exception as e:
        if str(e) != "{} has no leads".format(i):
            print("{} -- {}".format(i, str(e).upper()))

setter_report = SetterOfficeReport(handler = data)
setter_report.output()
print("Created Setter Office Report")

for i in data.setters:
    if i not in ["No Setter"]:
        try:
            report = SetterIndividualReport(i, handler = data)
            report.output()
            print("Setter Report Created for {}".format(i))
        except Exception as e:
            if str(e) != "{} has no leads".format(i):
                print(str(e).upper())
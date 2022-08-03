# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from CloserReport import IndividualReport, OfficeReport
from SetterReport import SetterIndividualReport, SetterOfficeReport
from DataHandler import DataHandler
import logging

data = DataHandler()

office_report = OfficeReport(handler = data)
office_report.output()
print("Created Closer Office Report")

for i in data.closers:
    if i not in ["Enerflo Admin", "No Owner"]:
        report = IndividualReport(i, handler = data)
        report.output()
        print("Closer Report Created for {}".format(i))

setter_report = SetterOfficeReport(handler = data)
setter_report.output()
print("Created Setter Office Report")

for i in data.setters:
    if i not in ["No Setter"]:
        report = SetterIndividualReport(i, handler = data)
        report.output()
        print("Setter Report Created for {}".format(i))
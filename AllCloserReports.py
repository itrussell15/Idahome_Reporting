# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

from ReportGenerator import IndividualReport, OfficeReport
from DataHandler import DataHandler

data = DataHandler("Data/Data.xlsx")
office = data.getOfficeData()
closers = office.leads["Lead Owner"].unique()

office_report = OfficeReport(office, handler = data)
office_report.output()

for i in closers:
    try:
        report = IndividualReport(i, handler = data)
        report.output()
        print("Created Report for {}".format(i))
    except:
        pass
        # print("**ERROR on {}***".format(i))
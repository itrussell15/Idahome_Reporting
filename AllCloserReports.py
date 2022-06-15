# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

from ReportGenerator import CloserReport
from DataHandler import DataHandler

data = DataHandler("Data/Data.xlsx")
office = data.getOfficeData("Idahome Electric")
closers = office.allClosers()

for i in closers:
    try:
        print("Creating Report for {}".format(i))
        report = CloserReport(i, handler = data)
    except:
        print("**ERROR on {}***".format(i))
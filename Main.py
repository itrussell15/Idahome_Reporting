# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 18:56:46 2022

@author: Schmuck
"""

import sys, os

sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/Data")
sys.path.append(os.getcwd() + "/Report")

# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 200)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from CloserReport import IndividualReport, OfficeReport
from SetterReport import SetterIndividualReport, SetterOfficeReport
import InstallReport

from DataHandler import DataHandler
import logging, traceback
import datetime

data = DataHandler(previous_weeks = 6)

try:
    report = OfficeReport(handler = data)
    report.output()
    print("Closer Office Report Generated")
except:
        logging.warning("Unable to create closer office report. Please see the exception:\n{}".format(traceback.format_exc()))

try:
    report = SetterOfficeReport(handler = data)
    report.output()
    print("Setter Office Report Generated\n")
except:
    logging.warning("Unable to create setter office report. Please see the exception:\n{}".format(traceback.format_exc()))
    
for i in data.closers:
    try:
        report = IndividualReport(i, handler = data)
        report.output()
        print("Closer Report Generated for {}".format(i))
    except:
        logging.warning("Unable to create report for {} Please see the exception:\n{}".format(i, traceback.format_exc()))

for i in data.setters:
    try:
        report = SetterIndividualReport(i, handler = data)
        report.output()
        print("Setter Report Generated for {}".format(i))
    except:
        logging.warning("Unable to create report for {} Please see the exception:\n{}".format(i, traceback.format_exc()))
    
try:
    report = InstallReport.OfficeReport(handler = data)
    report.output()
    print("Office Install Report Generated")
except:
    logging.warning("Unable to create office install report. Please see the exception:\n{}".format(i, traceback.format_exc()))

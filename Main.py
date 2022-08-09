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
import logging, traceback
import datetime


data = DataHandler(previous_weeks = 6)

for i in data.closers:
    try:
        report = IndividualReport(i, handler = data)
        report.output()
        print("Closer Report Generated for {}".format(i))
        # logging.info("R")
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
    report = OfficeReport(handler = data)
    report.output()
    print("Closer Office Report Generated")
except:
        logging.warning("Unable to create closer office report. Please see the exception:\n{}".format(i, traceback.format_exc()))
    
try:
    report = SetterOfficeReport(handler = data)
    report.output()
    print("Setter Office Report Generated")
except:
    logging.warning("Unable to create setter office report. Please see the exception:\n{}".format(i, traceback.format_exc()))
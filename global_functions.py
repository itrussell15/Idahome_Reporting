# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 10:39:45 2022

@author: Schmuck
"""

import os, sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def resource_base():
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path
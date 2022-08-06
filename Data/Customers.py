#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 22:03:48 2022

@author: isaactrussell
"""


class CustomerData:
    
    def __init__(self, name, data_obj):
        self.name = name
        self._data = data_obj.data
        
        self.numLeads = len(self._data)
        
    @property
    def data(self):
        return self._data
    
    # Only returns a number of pitched leads. See _getPitchedLeads for the DF with customer information
    @property
    def numPitched(self):
        return self.numSigns + self._getGroupedTotal("Pitched", self._status) + self._getGroupedTotal("Signed- Canceled", self._status)
        
class OfficeData(CustomerData):
    
    def __init__(self, data_obj):
        super().__init__("Office", data_obj)
        
        self.closers = data_obj.closers
        self.setters = data_obj.setters
        
class OfficeCloserData(OfficeData):
    
    def __init__(self, data_obj):
        super().__init__(data_obj)
        
class OfficeSetterData(OfficeData):
    
    def __init__(self, data_obj):
        super().__init__(data_obj)
        
class IndvData(CustomerData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        
    def maskIndvData(self, name, job_type):
        return self._data[self._data[job_type] == name]
    
class IndvCloserData(IndvData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        
        if name in data_obj.closers:
            self._data = self.maskIndvData(name, "closer")
        else:
            # Might not need to raise could be log
            raise ValueError("{} has no leads in this data".format(self.name))
            
class IndvSetterData(IndvData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        self._data = self.maskIndvData(name, "setter")

        if name in data_obj.setters:
            self._data = self.maskIndvData(name, "setter")
        else:
            raise ValueError("{} has no leads in this data".format(self.name))
                
        
if __name__ == "__main__":
    from DataHandler import DataHandler
    
    data = DataHandler(previous_weeks = 1)
    closer = IndvCloserData("Zach Trussell", data.customers)
    setter = IndvSetterData("Kyle Wagner", data.customers)        
        
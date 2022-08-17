#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 22:03:48 2022

@author: isaactrussell
"""

import pandas as pd
import datetime 
import logging
from ReportableData import BaseData

class CustomerData(BaseData):
    
    def __init__(self, name, data_obj):
        super().__init__(data_obj)
        self.name = name
        
        self._data = self._importDates(self._data)
        
    def _importDataFrame(self, data):
        return data    

    def _importDates(self, data):
                
        # TODO Convert datetimes from strings to be able to use  
        for i in ["created", "nextApptDate"]:
            if data[i].dtype == object:
                data[i] = pd.to_datetime(data[i], errors = "coerce")
        return data    

    @property
    def numLeads(self):
        value = len(self._data)
        return value if value else 0

    @property
    def numPitched(self):
        column = "lead_status"
        value = self.numSigns + \
            len(self.groupedOutput("Pitched", column))  + \
            len(self.groupedOutput("Signed- Canceled", column))
        return value if value else 0
    
    @property
    def numSigns(self):
        value = len(self.groupedOutput("Signed", "lead_status"))
        return value if value else 0
    
    @property
    def numNoShow(self):
        noShow = self.groupedOutput("No Show", "lead_status")
        cancel = self.groupedOutput("Canceled", "lead_status")
        total = len(noShow) + len(cancel)
        return total if total else 0
    
    @property
    def closeRatio(self):
        return self._potentialDivisionError(self.numSigns, self.numPitched)
    
    @property
    def closeRatioTotal(self):
        return self._potentialDivisionError(self.numSigns, self.numLeads)
    
    @property
    def pitchRatio(self):
        return self._potentialDivisionError(self.numPitched, self.numLeads)
    
    @property
    def pullThroughRatio(self):
        signedCanceled = len(self.groupedOutput("Signed- Canceled", "lead_status"))
        return self._potentialDivisionError(self.numSigns, self.numPitched + signedCanceled)
    
    @property
    def cancelRatio(self):
        return self._potentialDivisionError(self.numNoShow, self.numLeads)
    
    # Shows the conversion efficiency of various lead methods
    @property
    def finalTable(self):
        sources = list(self._data.lead_source.unique())
        output = []
        for i in sources:
            source_leads = self.data[self.data["lead_source"] == i]
            signed_leads = self.subGroupedOutput("Signed", "lead_status", source_leads)
            pitched_leads = self.subGroupedOutput("Pitched", "lead_status", source_leads)
            sign_cancel_leads = self.subGroupedOutput("Signed- Canceled", "lead_status", source_leads)
            pitched_leads = pd.concat([signed_leads, pitched_leads, sign_cancel_leads])
            output.append({"Source": i, "Leads": len(source_leads), "Pitched": len(pitched_leads), "Signs": len(signed_leads)})
            
        df = pd.DataFrame.from_records(output).set_index("Source")
        df["Pitched %"] = 100*(df["Pitched"]/df["Leads"]).round(2)
        df["Pitch-Signed"] = 100*(df["Signs"]/df["Pitched"]).round(2)
        df["Lead-Signed"] = 100*(df["Signs"]/df["Leads"]).round(2)
        totals = [self.numLeads, self.numPitched, self.numSigns,
                  self.pitchRatio, self.closeRatio, self.closeRatioTotal]
        df.loc["Totals"] = totals
        df.fillna(0, inplace = True)
        df.reset_index(inplace = True)
        for i in ["Leads", "Pitched", "Signs"]:
            df[i] = df[i].astype(int)
        
        for i in ["Pitched %", "Pitch-Signed", "Lead-Signed"]:
            df[i] = df[i].apply(lambda x: "{:.2f}".format(x))
        return df
    
    @property
    def customerTable(self):

        data = self.data[["name", "lead_source", "lead_status", "closer", "setter", "created", "nextApptDate"]].copy()
        
        data["lead_status"].fillna("No Dispo", inplace = True)
        data["lead_source"].fillna("No Source", inplace = True)
        data["name"].fillna("No Name", inplace = True)
        # print(data.dtypes)
        data["created"] = data["created"].apply(self.formatDate)
        data["nextApptDate"] = data["nextApptDate"].apply(self.formatDatetime)
        data["nextApptDate"].fillna("-", inplace = True)
        data["setter"].replace("Austin Anderson- Call Center", "Austin Anderson", inplace = True)
        data["lead_source"].replace("Website/Called In", "Website", inplace = True) 
        data["lead_status"].replace("Signed- Canceled", "Sign-Cancel", inplace = True) 
        data.sort_values(by = "created", ascending = False, inplace = True)    
        data.columns = ["Customer", "Source", "Status", "Closer", "Setter", "Created", "Next Appt"]   

        return data
    
    @property
    def KPIs(self):
        columns = ["Total Leads", "Lead-Pitched",  "% No Show"]
        data = [str(i) for i in [self.numLeads, self.pitchRatio,  self.cancelRatio]]
        return [columns, data]
    
    def groupedOutput(self, value, column):
        return self.data[self.data[column] == value]
        
    @staticmethod
    def subGroupedOutput(value, column, subdata):
        return subdata[subdata[column] == value]
    
    # Handles potential ZeroDivisionErrors while running the rep
    def _potentialDivisionError(self, num, denom, percentage = True):
        try:
            if percentage:
                return round(100 * (num/denom), 2)
            else:
                return num/denom
        except ZeroDivisionError:
            logging.warning("Division Error Avoided on {}".format(self.name))
            return 0
        except:
            raise ValueError("Non ZeroDivisionError occured")
    
    # @staticmethod    
    # def formatDate(x):
    #     if x is not pd.NaT:
    #         return x.strftime("%m-%d-%Y")
    #     else:
    #         return None
    
    # @staticmethod
    # def formatDatetime(x):
    #     if x is not pd.NaT:
    #         return x.strftime("%m-%d-%Y %I%p")
    #     else:
    #         return None
        
class OfficeData(CustomerData):
    
    def __init__(self, data_obj):
        super().__init__("Office", data_obj)
        
        # self.closers = data_obj.closers
        # self.setters = data_obj.setters
        
class OfficeCloserData(OfficeData):
    
    def __init__(self, data_obj):
        super().__init__(data_obj)
        
    @property
    def summaryTable(self):
        collection = []
        for i in self.closers:
            closer = IndvCloserData(i, self._data)
            temp = {"Closer": i, "Leads": closer.numLeads, "Pitched": closer.numPitched, "Signs": closer.numSigns,
                    "Pitched %": closer.pitchRatio, "Pitched-Signed": closer.closeRatio, "Lead-Signed": closer.closeRatioTotal}
            collection.append(temp)
        df = pd.DataFrame.from_records(collection)
        df.sort_values(by = "Leads", inplace = True, ascending = False)
        return df
        
    
    @property
    def customerTable(self):
        table = CustomerData.customerTable.fget(self)
        table = table[["Customer", "Source", "Status", "Closer"]]
        table.sort_values(by = "Closer", inplace = True)
        return table
    
    @property
    def closerLeadGeneration(self):
        everything = pd.DataFrame()
        for closer in self.data["closer"].unique():
            # if closer not in ["Enerflo Admin", "No Owner"]:
            closerData = self.data[self.data["closer"] == closer].groupby("lead_source")["name"].count()
            closerData.name = closer
            everything = pd.concat([everything, closerData], axis = 1)
            
        try:
            everything.drop("Enerflo Admin", axis = 0, inplace = True)
        except:
            pass
            
        everything = everything.transpose()
        everything.fillna(0.0, inplace = True)
        everything["Last 6 Wks"] = everything.sum(axis = 1)
        everything.sort_values(by = "Last 6 Wks", ascending = False, inplace = True)

        # Bring Last 6 weeks to the left
        cols = everything.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        everything = everything[cols]
        
        everything.loc["Totals"] = everything.copy().sum().values
        everything = everything.astype(int)
        
        everything.drop(0, inplace = True)
        everything.reset_index(inplace = True)
        everything = everything.rename(columns = {'index':'Closer',
                                      "Website/Called In": "Website",
                                      "Sales Rabbit": "Sales Rbt"})
        return everything
    
    @property
    def closerLeadStatus(self):
        everything = pd.DataFrame()
        for closer in self.data["closer"].unique():
            if closer not in ["Enerflo Admin", "No Owner"]:
                closerData = self.data[self.data["closer"] == closer].groupby("lead_status")["name"].count()
                closerData.name = closer
                everything = pd.concat([everything, closerData], axis = 1)
        
        everything = everything.transpose()
        everything.fillna(0.0, inplace = True)
        everything["sum"] = everything.sum(axis = 1)
        everything.sort_values(by = "sum", ascending = False, inplace = True)
        everything.drop("sum", axis = 1, inplace = True)
        everything.drop(0, inplace = True)
        everything.loc["Totals"] = everything.copy().sum().values
        everything = everything.astype(int)
        
        for_totals = everything.copy().sum().values
        everything.loc["Percentages"] = ["{:.2f}%".format(100*i) for i in for_totals/sum(for_totals)]
        everything.rename(columns = {"Signed- Canceled": "Sign-Cancel"}, inplace = True)
        return everything.reset_index()
        
class OfficeSetterData(OfficeData):
    
    def __init__(self, data_obj):
        super().__init__(data_obj)
        
    @property
    def customerTable(self):
        table = CustomerData.customerTable.fget(self)
        table = table[["Customer", "Source", "Status", "Setter", "Next Appt"]]
        table.dropna(inplace = True)
        table.sort_values(by = "Setter", inplace = True)
        return table
        
class IndvData(CustomerData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        
    def maskIndvData(self, name, job_type):
        data = self._data[self._data[job_type] == name].copy()
        data.drop(job_type, axis = 1, inplace = True)
        return data
    
    @property
    def customerTable(self):
        table = CustomerData.customerTable.fget(self)
        table = table[["Customer", "Source", "Status"]]
        return table
    
class IndvCloserData(IndvData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        
        self._customerTable = CustomerData.customerTable.fget(self)
        
        if name in self.closers:
            self._data = self.maskIndvData(name, "closer")
        else:
            # Might not need to raise could be log
            raise ValueError("{} has no leads in this data".format(self.name))
            
    @property
    def customerTable(self):
        table = self._customerTable.copy()
        table = table[["Customer", "Source", "Status"]]
        return table
        
class IndvSetterData(IndvData):
    
    def __init__(self, name, data_obj):
        super().__init__(name, data_obj)
        
        self._customerTable = CustomerData.customerTable.fget(self)
        
        if name in self.setters:
            self._data = self.maskIndvData(name, "setter")
        else:
            raise ValueError("{} has no leads in this data".format(self.name))
                 
    @property
    def customerTable(self):
        table = self._customerTable.copy()
        table = table[["Customer", "Status", "Created", "Next Appt"]]
        table = table.replace("Signed- Canceled", "Sign-Cancel")
        return table
        
if __name__ == "__main__":
    from DataHandler import DataHandler
    
    data = DataHandler(previous_weeks = 4)
    office = OfficeCloserData(data)
    print(office.summaryTable)
    # closer = IndvCloserData("Darren Phillips", data)
    # setter = IndvSetterData("Kyle Wagner", data.customers) 
    
    # print(office.customerTable.head())
    # print(closer.data.head())
    
        
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""
# %% Imports
import pandas as pd
import os, datetime
import matplotlib.pyplot as plt
import matplotlib

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 200)

# %% Data Handler
class DataHandler:

    def __init__(self, data_path):
        self._df = pd.read_excel(data_path)
        self._df["Lead Status"].fillna("No Dispo", inplace = True)
        self._df["Lead Source"].fillna("No Lead Source", inplace = True)
        self._df["Lead Owner"].fillna("No Owner", inplace = True)
        self._df["Setter"].fillna("No Setter", inplace = True)
        self._df["Office"].fillna("No Office", inplace = True)
        
        self.closers = self._getClosers()
        self.setters = self._getSetters()
        
    def _getClosers(self):
        return self._getUnique("Lead Owner")
    
    def _getSetters(self):
        return self._getUnique("Setter")
    
    def _getUnique(self, column):
        return self._df[column].unique()
    
    def getCloserData(self, name = None):
        if name:
            if name in self._getClosers():
                closerData = self._df.loc[self._df["Lead Owner"] == name].copy()
                closerData.drop("Lead Owner", axis = 1, inplace = True)
                return self._InvidualData(name, closerData)
            else:
                raise KeyError("{} has no leads in this data".format(name))
        else:
            return self._OfficeData(self._df.copy())
        
    def getSetterData(self, name = None):
        
        if name:
            
            if name in self._getSetters():
                setterData = self._df.loc[self._df["Setter"] == name].copy()
                setterData.drop("Setter", axis = 1, inplace = True)
                return self._SetterIndvData(name, setterData)
        else:
            return self._SetterOfficeData(self._df.copy())

# %% Reportable Data Class
    class _ReportableData:

        def __init__(self, name, raw_data, previous_weeks = 6):
            self.name = name
            
            if previous_weeks:
                today = datetime.datetime.today()
                self.leads = raw_data[raw_data["Added"] >= today - datetime.timedelta(weeks = previous_weeks)]
            else:
                self.leads = raw_data
                
            self._source = self._groupedOutput("Lead Source")
            self._status = self._groupedOutput("Lead Status")
            
            # Can drop all the duplicates
            # self.duplicated = self.leads[self.leads.duplicated("Customer")]
            # self.leads = self.leads.drop_duplicates(subset = "Customer", keep = "first").copy()
    
        def _groupedOutput(self, column):
            output = self.leads.groupby(column).count()["ID"]
            output.rename(self.name, inplace = True)
            return output
        
        # Requires a grouping as an input to be to return a total
        @staticmethod
        def _getGroupedTotal(value, group):
            try:
                return group.loc[value]
            except:
                # print("{} not found in grouping")
                return 0        
            
        # Handles potential ZeroDivisionErrors while running the rep
        @staticmethod
        def _potentialDivisionError(num, denom, percentage = True):
            try:
                if percentage:
                    return 100 * (num/denom)
                else:
                    return num/denom
            except ZeroDivisionError:
                return 0
            except:
                raise ValueError("Non ZeroDivisionError occured")

        # Only returns a number of pitched leads. See _getPitchedLeads for the DF with customer information
        def _getPitched(self):
            return self.numSigns + self._getGroupedTotal("Pitched", self._status) + self._getGroupedTotal("Signed- Canceled", self._status)

        # Gets all sits, which includes multiple disposition categories
        def _getPitchedLeads(self, source_leads):
            everything = pd.DataFrame()
            for i in ["Signed", "Singed- Canceled", "Pitched"]:
                try:
                    to_add = source_leads[source_leads["Lead Status"] == i]
                    everything = pd.concat([everything, to_add])
                except AttributeError:
                    print("No Attribute {}".format(i))
            return everything
        
# %% Closers Classes
    class _CloserData(_ReportableData):
        
        def __init__(self, name, raw_data, previous_weeks = 6):
            super().__init__(name, raw_data, previous_weeks)
            
            
            self.numSelfGens = self._getGroupedTotal("Self Gen", self._source)
            self.numSigns = self._getGroupedTotal("Signed", self._status)
            self.numLeads = len(self.leads) - self.numSelfGens
            self.numSits = self._getPitched()
            
            self.closeRatio = self._potentialDivisionError(self.numSigns, self.numSits)
            self.closeRatioTotal = self._potentialDivisionError(self.numSigns, self.numLeads)
            self.pitchRatio = self._potentialDivisionError(self.numSits, self.numLeads)
            self.pullThroughRatio = self._potentialDivisionError(self.numSigns, (self.numSigns + self._getGroupedTotal("Signed- Canceled", self._status)))
            
            self.finalTable = self._finalTable()
            
        def __repr__(self):
            return self.leads

        # Shows the conversion efficiency of various lead methods
        def _finalTable(self):
            
            sources = list(self._source.index)
            output = []
            for i in sources:
                
                source_leads = self.leads[self.leads["Lead Source"] == i]
                signed_leads = source_leads[source_leads["Lead Status"] == "Signed"]
                pitched_leads = self._getPitchedLeads(source_leads)
                output.append({"Source": i, "Leads": len(source_leads), "Pitched": len(pitched_leads), "Signs": len(signed_leads)})
                
            df = pd.DataFrame.from_records(output).set_index("Source")
            df["Pitched %"] = 100*(df["Pitched"]/df["Leads"])
            df["Pitch-Signed"] = 100*(df["Signs"]/df["Pitched"])
            df["Lead-Signed"] = 100*(df["Signs"]/df["Leads"])
            df.fillna(0, inplace = True)
            
            return df

    class _InvidualData(_CloserData):

        def __init__(self, closer_name, data):
            super().__init__(closer_name, data)

    class _OfficeData(_CloserData):

        def __init__(self, data):
            super().__init__("Office", data)
            
        def closerLeadGeneration(self):
            everything = pd.DataFrame()
            for closer in self.leads["Lead Owner"].unique():
                # if closer not in ["Enerflo Admin", "No Owner"]:
                closerData = self.leads[self.leads["Lead Owner"] == closer].groupby("Lead Source")["ID"].count()
                closerData.name = closer
                everything = pd.concat([everything, closerData], axis = 1)
                
            everything = everything.transpose()
            everything.fillna(0.0, inplace = True)
            everything["Last 6 Wks"] = everything.sum(axis = 1)
            everything.sort_values(by = "Last 6 Wks", ascending = False, inplace = True)
            
            try:
                everything.drop("Enerflo Admin", axis = 0, inplace = True)
            except:
                pass

            # Bring Last 6 weeks to the left
            cols = everything.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            everything = everything[cols]
            
            return everything
        
        def closerLeadStatus(self):
            everything = pd.DataFrame()
            for closer in self.leads["Lead Owner"].unique():
                if closer not in ["Enerflo Admin", "No Owner"]:
                    closerData = self.leads[self.leads["Lead Owner"] == closer].groupby("Lead Status")["ID"].count()
                    closerData.name = closer
                    everything = pd.concat([everything, closerData], axis = 1)
            
            everything = everything.transpose()
            everything.fillna(0.0, inplace = True)
            everything["sum"] = everything.sum(axis = 1)
            everything.sort_values(by = "sum", ascending = False, inplace = True)
            everything.drop("sum", axis = 1, inplace = True)
            try:
                everything.drop("Enerflo Admin", axis = 0, inplace = True)
            except:
                pass
            
            cols = ["Pitched", "Not Pitched", "Canceled", "No Show", "Signed", "Signed- Canceled", "DNQ", "No Dispo"]
            everything = everything[cols]
            return everything        
# %% Setters Classes

    class _SetterData(_ReportableData):
        
        def __init__(self, name, raw_data, previous_weeks = 6):
            super().__init__(name, raw_data, previous_weeks)
            
    class _SetterIndvData(_SetterData):

        def __init__(self, setter_name, data):
            super().__init__(setter_name, data)
            
    class _SetterOfficeData(_SetterData):

        def __init__(self, data):
            super().__init__("Office", data)
            

#%% Main
if __name__ == "__main__":
    data = DataHandler(os.getcwd() + "/Data/Data.xlsx")
    # setters = data.getSetterData()
    setter = data.getSetterData("Jake Hagerty")
    # out = data.getCloserData("Cole Newell")
    # office = data.getCloserData()
    # counts = office.closerLeadStatus()
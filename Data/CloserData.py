# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 14:48:06 2022

@author: Schmuck
"""

import pandas as pd
from ReportableData import ReportableData

class _CloserData(ReportableData):
    
    def __init__(self, name, raw_data, previous_weeks = 6):
        super().__init__(name, raw_data, previous_weeks)

        self.numSelfGens = self._getGroupedTotal("Self Gen", self._source)
        self.numSigns = self._getGroupedTotal("Signed", self._status)

        self.numLeads = len(self.leads)
        self.numPitched = self._getPitched()
        
        self.closeRatio = self._potentialDivisionError(self.numSigns, self.numPitched)
        self.closeRatioTotal = self._potentialDivisionError(self.numSigns, self.numLeads)
        self.pitchRatio = self._potentialDivisionError(self.numPitched, self.numLeads)
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

class InvidualData(_CloserData):

    def __init__(self, closer_name, data):
        super().__init__(closer_name, data)

class OfficeData(_CloserData):

    def __init__(self, data):
        super().__init__("Office", data)
        
        self.setters = self.leads["Setter"].unique()
        self.closers = self.leads["Lead Owner"].unique()
        
        print(self.leads)
        
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
        
        output = pd.DataFrame()
        cols = ["Pitched", "Not Pitched", "Canceled", "No Show", "Signed", "Signed- Canceled", "DNQ", "No Dispo"]
        for i in cols:
            try:
                if output.empty:
                    output = everything[i].copy()
                else:
                    output = pd.concat([output, everything[i]], axis = 1)
            except:
                pass

        return output    
    
if __name__ == "__main__":
    pass
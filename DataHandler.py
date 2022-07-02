# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""

import pandas as pd
import os, datetime
import matplotlib.pyplot as plt
import matplotlib
from global_functions import *
import logging

class DataHandler:

    def __init__(self, data_path):
        path = resource_path(data_path)
        self.df = pd.read_excel(path)
        self.df["Lead Status"].fillna("Disposition Not Set", inplace = True)
        self.df["Lead Source"].fillna("No Lead Source", inplace = True)
        self.df["Lead Owner"].fillna("No Owner", inplace = True)
        self.df["Office"].fillna("No Office", inplace = True)

    def getCloserData(self, name):
        if name in self.df["Lead Owner"].unique():
            closerData = self.df.loc[self.df["Lead Owner"] == name].copy()
            closerData.drop("Lead Owner", axis = 1, inplace = True)
            return self._CloserData(name, closerData)
        else:
            raise KeyError("{} has no leads in this data".format(name))

    # def getOfficeData(self, name):
    #     if name in self.df["Office"].unique():
    #         officeData = self.df.loc[self.df["Office"] == name].copy()
    #         officeData.drop("Office", axis = 1, inplace = True)
    #         return self._OfficeData(name, officeData)
    #     else:
    #         raise KeyError('{} has no leads in this data'.format(name))

    def getOfficeData(self):
        return self._OfficeData(self.df.copy())

    class _ReportableData:

        def __init__(self, name, raw_data, previous_weeks = 6):
            self.name = name
            
            if previous_weeks:
                today = datetime.datetime.today()
                self.leads = raw_data[raw_data["Added"] >= today - datetime.timedelta(weeks = previous_weeks)]
            else:
                self.leads = raw_data
            
            # Can drop all the duplicates
            # self.duplicated = self.leads[self.leads.duplicated("Customer")]
            # self.leads = self.leads.drop_duplicates(subset = "Customer", keep = "first").copy()
    
            self._source = self._groupedOutput("Lead Source")
            self._status = self._groupedOutput("Lead Status")
            
            self.numSelfGens = self._getGroupedTotal("Self Gen", self._source)
            self.numSigns = self._getGroupedTotal("Signed", self._status)
            self.numLeads = len(self.leads) - self.numSelfGens
            self.numSits = self._getPitched()

            self.closeRatio = 100 * (self.numSigns/self.numSits)
            self.closeRatioTotal = 100 * (self.numSigns/self.numLeads)
            self.pitchRatio = 100 * (self.numSits/self.numLeads)
            self.pullThroughRatio = 100 * (self.numSigns/(self.numSigns + self._getGroupedTotal("Signed- Canceled", self._status)))
            
            self.finalTable = self._finalTable()
            
        # Shows the conversion efficiency of various lead methods
        def _finalTable(self):
            
            sources = list(self._source.index)
            output = []
            for i in sources:
                
                source_leads = self.leads[self.leads["Lead Source"] == i]
                signed_leads = source_leads[source_leads["Lead Status"] == "Signed"]
                pitched_leads = self._getPitchedLeads(source_leads)
                output.append({"Source": i, "Leads": len(source_leads), "Signs": len(signed_leads), "Pitched": len(pitched_leads)})
                
            df = pd.DataFrame.from_records(output).set_index("Source")
            df["Pitched %"] = 100*(df["Pitched"]/df["Leads"])
            df["Pitch-Signed"] = 100*(df["Signs"]/df["Pitched"])
            df["Lead-Signed"] = 100*(df["Signs"]/df["Leads"])
            df.fillna(0, inplace = True)
            
            return df
                
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

        def byGeneration(self):
            return self._groupedOutput("Lead Source")

        def graphGeneration(self,
                            title = None,
                            percentages = False,
                            color = "orange",
                            save_image = False,
                            path = "/assets/temp",):
            self._graphByGrouped("Lead Source", title, percentages, color, save_image)

        def byDisposition(self):
            return self._groupedOutput("Lead Status")

        def graphDisposition(self,
                             title = None,
                             percentages = False,
                             color = "orange",
                             save_image = False,
                             path = "/assets/temp",):
            self._graphByGrouped("Lead Status", title, percentages, color, save_image)
            
        def _graphByGrouped(self, column,
                            title,
                            percentages = False,
                            color = "b",
                            save_image = False,
                            path = "/assets/temp",
                            ):
            data = self._groupedOutput(column)
            fig = plt.figure(figsize = (50, 50))
            ax = plt.subplot(111)
            # plt.title("{}'s {}s".format(self.name, column))
            graph = ax.barh(data.index, data.values, color = color, alpha = 0.8)
            # graph = ax.bar(data.index, data.values, color = color)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if percentages:
                i = 0
                percentages = 100*(data.values/sum(data.values))
                for p in graph:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                    ax.text(x+width*1.05,
                              y+height/2,
                              "{:.2f}%".format(percentages[i]),
                              ha='center',
                              weight='bold')
                    i+=1

            if save_image:
                # print(__name__)
                if __name__ != "__main__":
                    path = "{}/{}.png".format(path, title)
                else:
                    path = "{}/{}_{}.png".format(path, self.name, column)
                figure = plt.gcf() # get current figure
                figure.set_size_inches(18, 8)
                plt.savefig(resource_path(path), dpi = 100)
                plt.close()

    class _CloserData(_ReportableData):

        def __init__(self, closer_name, data):
            super().__init__(closer_name, data)

    class _OfficeData(_ReportableData):

        def __init__(self, data):
            super().__init__("All", data)
            
        def closerLeadGeneration(self):
            everything = pd.DataFrame()
            for closer in self.leads["Lead Owner"].unique():
                closerData = self.leads[self.leads["Lead Owner"] == closer].groupby("Lead Source")["ID"].count()
                closerData.name = closer
                everything = pd.concat([everything, closerData], axis = 1)
                
            everything = everything.transpose()
            everything.fillna(0.0, inplace = True)
            everything.drop("No Owner", inplace = True)
            everything["Last 6 Wks"] = everything.sum(axis = 1)
            everything.sort_values(by = "Last 6 Wks", ascending = False, inplace = True)
            return everything

if __name__ == "__main__":
    data = DataHandler("Data/Data.xlsx")
    office = data.getOfficeData()
    counts = office.closerLeadGeneration()
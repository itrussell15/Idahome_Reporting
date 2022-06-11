# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

class DataHandler:

    def __init__(self, data_path):
        self.df = pd.read_excel(data_path)
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

    def getOfficeData(self, name):
        if name in self.df["Office"].unique():
            officeData = self.df.loc[self.df["Office"] == name].copy()
            officeData.drop("Office", axis = 1, inplace = True)
            return self._OfficeData(name, officeData)
        else:
            raise KeyError('{} has no leads in this data'.format(name))
            
    def getAllData(self):
        return self._AllData(self.df.copy())
    
    class _ReportableData:

        def __init__(self, name, raw_data):
            self.name = name
            self.leads = raw_data
            self.numSigns = self._getSigns()
            self.numLeads = len(self.leads)
            self.closeRatio = 100*(self.numSigns/self.numLeads)
    
        def _groupedOutput(self, column):
            output = self.leads.groupby(column).count()["ID"]
            output.rename(self.name, inplace = True)
            return output
        
        def _graphByGrouped(self, column, percentages = False, color = "b", save_image = False):
            data = self._groupedOutput(column)
            fig = plt.figure(figsize = (50, 50))
            ax = plt.subplot(111)
            plt.title("{}'s {}s".format(self.name, column))
            graph = ax.barh(data.index, data.values, color = color)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if percentages:
                i = 0
                percentages = 100*(data.values/sum(data.values))
                for p in graph:
                    width = p.get_width()
                    height = p.get_height()
                    x, y = p.get_xy()
                    ax.text(x+width+2,
                              y+height/2,
                              "{:.2f}%".format(percentages[i]),
                              ha='center',
                              weight='bold')
                    i+=1
                    
            if save_image:
                print("HERE")
                plt.savefig(os.getcwd() + "/assets/{}_{}.png".format(self.name, column), dpi = 100)
        
        def _getSigns(self):
            return self._groupedOutput("Lead Status")["Signed"]
        
        def byGeneration(self):
            return self._groupedOutput("Lead Source")
        
        def graphGeneration(self, percentages = False, color = "orange", save_image = False):
            self._graphByGrouped("Lead Source", percentages, color, save_image)
        
        def byDisposition(self):
            return self._groupedOutput("Lead Status")
        
        def graphDisposition(self, percentages = False, color = "orange", save_image = False):
            self._graphByGrouped("Lead Status", percentages, color, save_image)
    
    class _CloserData(_ReportableData):

        def __init__(self, closer_name, data):
            super().__init__(closer_name, data)
            
        
    class _OfficeData(_ReportableData):

        def __init__(self, officeName, data):
            super().__init__(officeName, data)
            
        def byCloser(self):
            return super()._groupedOutput("Lead Owner")
        
        def graphCloser(self, percentages = False, color = "orange", save_image = False):
            self._graphByGrouped("Lead Owner", percentages, color, save_image)    
            
    class _AllData(_ReportableData):
        
        def __init__(self, data):
            super().__init__("All", data)



if __name__ == "__main__":
    
    data = DataHandler(os.getcwd() + "/Data/Data.xlsx")
    # z = data.getCloserData("Zach Trussell")
    # z.graphGeneration(True)
    office = data.getOfficeData("Idahome Electric")
    office.graphCloser(True, save_image = True)
    # office.graphDisposition(True, "g")

    # z = data.getCloserData("Zach Trussell")
    # print(z.byDisposition())


# pieces = dispo["Zach Trussell"][dispo["Zach Trussell"] > 0]
# graph = axes[0].barh(pieces.index, pieces.values)
# axes[0].spines['right'].set_visible(False)
# axes[0].spines['top'].set_visible(False)
# axes[0].set_title("Dispositions")
# addPercentages(graph, pieces, axes[0])

# pieces = generation["Zach Trussell"][generation["Zach Trussell"] > 0]
# graph = axes[1].barh(pieces.index, pieces.values)
# axes[1].spines['right'].set_visible(False)
# axes[1].spines['top'].set_visible(False)
# axes[1].set_title("Generation")
# addPercentages(graph, pieces, axes[1])

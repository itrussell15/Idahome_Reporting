# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 22:57:51 2022

@author: Schmuck
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

df = pd.read_excel(os.getcwd() + "/Data/Data.xlsx")
df["Lead Status"].fillna("Disposition Not Set", inplace = True)
df["Lead Source"].fillna("No Lead Source", inplace = True)
df["Lead Owner"].fillna("No Owner", inplace = True)

owners = df["Lead Owner"].unique()
byStatus = df.groupby(["Lead Owner", "Lead Status"]).size()
byGen  = df.groupby(["Lead Owner", "Lead Source"]).size()

disposition = {}
generation = {}
for i in owners:
    disposition.update({i: byStatus[i].to_dict()})
    generation.update({i: byGen[i].to_dict()})


dispo = pd.DataFrame.from_records(disposition)
generation = pd.DataFrame.from_records(generation)
dispo.fillna(0, inplace = True)
generation.fillna(0, inplace = True)

fig, axes = plt.subplots(1, 2)
fig.suptitle("Zach Trussell")

def addPercentages(graph, data, axis):
    i = 0
    percentages = 100*(data.values/sum(data.values))
    for p in graph:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        axis.text(x+width+4,
                 y+height/2,
                 "{:.2f}%".format(percentages[i]),
                 ha='center',
                 weight='bold')
        i+=1

pieces = dispo["Zach Trussell"][dispo["Zach Trussell"] > 0]
graph = axes[0].barh(pieces.index, pieces.values)
axes[0].spines['right'].set_visible(False)
axes[0].spines['top'].set_visible(False)
axes[0].set_title("Dispositions")
addPercentages(graph, pieces, axes[0])

pieces = generation["Zach Trussell"][generation["Zach Trussell"] > 0]
graph = axes[1].barh(pieces.index, pieces.values)
axes[1].spines['right'].set_visible(False)
axes[1].spines['top'].set_visible(False)
axes[1].set_title("Generation")
addPercentages(graph, pieces, axes[1])


    
# pieces = generation["Zach Trussell"][generation["Zach Trussell"] > 0]
# axes[1].pie(pieces.values, labels = pieces.index, autopct = "%1.1f%%")

# plt.pie(pieces.values, labels = pieces.index, autopct = "%1.1f%%")
# plt.title("Zach Trussell Disposition Breakdown")
'''
@Usage:
python 

@author: Claire-Sophie Devignes
@copyright: Institut des sciences du Digital, Management & Cognition – IDMC
@license: MIT License
@version: 1.0
@email: claire-sophie.devignes9@etu.univ-lorraine.fr
@date: 
'''
import logging

import pandas as pd

import EDA
import note, trace, merger, steplnr
import features as ft
import matplotlib.pyplot as plt


## Loading source files
print("Logarche program - Analysis of log files from Arche")
gradepath = input("Enter path to grade file (leave empty to load default file) :")
try:
    if gradepath == "":
        n = note.Note().data
    else:
        n = note.Note(gradepath).data
    print(f"Grades loaded for {len(n)} students.")
except:
    logging.warning("Error with grade file.")

logpath = input("Enter path to log file (leave empty to load default file) :")
try:
    if gradepath == "":
        t = trace.Trace().data
    else:
        t = trace.Trace(gradepath).data
    print(f"Logs loaded : {len(t)} entries.")
except:
    logging.warning("Error with log file.")

## Feature extraction
print("\nExtracting features...\n")
f_inter = ft.Interactions(t)
f_inter.inter_per_day_mean()
f_inter.inter_per_day_var()
f_inter.variete()
f_inter.count_afterhour_interaction()
f_inter.count_dayoff_interaction()
f_inter.count_interaction()
f_inter.day_with_inter()
f_type = ft.InteractionType(t)
f_type.evenements()
f_type.composant()
f_mat = ft.Materials(t)
f_mat.td()
f_mat.alltd()
f_mat.course_access()
f_time = ft.UserTime(t)
f_time.session_time_record()
f_time.session_sum()
f_time.session_avg()
# Merge of all feature with note data
m = merger.Merger(n, "feature/").data
## Exploratory data analysis
explo = EDA.EDA(m)
wgraph = 0
while wgraph != 3:
    wgraph = int(input("\nWhat would you like to explore ?\n1 - Distribution\n2 - Correlation\n3 - Stop exploring and go to machine learning\nYour choice: "))
    if wgraph == 1:
        datatype = int(input("\nDistribution graph of :\n1 - All features\n2 - All features normalized\nYour choice:"))
        if datatype == 1:
            dataplot = explo.data
        if datatype == 2:
            dataplot = explo.dataN
        explo.boxplot(dataplot.loc[:, dataplot.columns != 'note'])
    if wgraph ==2:
        corrtype = int(input("\nWould you like to keep highly correlated columns ?\n1 - Yes, keep everything\n2 - No, exclude them\nYour choice:"))
        if corrtype == 1:
            excludedCol = ["success", "mention"]
        if corrtype == 2:
            excludedCol = ["success", "mention", "comp_devoir", "comp_fichier", "comp_feedback", "comp_presence",
                           "comp_remises", "comp_systeme", "c_TD_all", "interactions", "ev_class_access"]
        explo.correlation(excludedCol)
## Linear regression
# Columns excluded because of high correlaction with other features
excludedCol = ["success", "mention", "comp_devoir", "comp_fichier", "comp_feedback", "comp_presence", "comp_remises",
               "comp_systeme", "c_TD_all", "interactions", "ev_class_access"]
varCol = [col for col in explo.data.columns if col not in excludedCol]
model = steplnr.CalculateModel(explo.data[varCol])
## Backward selection of the model
colToDelete = ""
savedmodels = pd.DataFrame(columns=["Model", "Features"])
i = 1
while colToDelete != "STOP":
      model.calculate()
      colToDelete = input("Which feature would you like to remove ? Save and continue: enter SAVE, "
                          "Save and stop: enter STOP\nEnter feature name :")
      if colToDelete == "SAVE":
          savedmodels.loc[len(savedmodels)] = [f'Model {i}', model.X.columns]
          print(savedmodels.loc[[i-1]])
          i = i+1
      if colToDelete in model.X:
          model.X = model.X.drop(columns=colToDelete)
savedmodels.loc[len(savedmodels)] = [f'Model {i}', model.X.columns]

## Cross validation
print("Models selected : ")
print(savedmodels)
# excludedCol1 = excludedCol + ["ev_presence_check", "day_with_inter", "ev_presence_set", "session_sum"]
# excludedCol2 = excludedCol1 + ["c_notTD", "c_TD5", "ev_course_access", "c_TD7", "ev_homework_status"]
# excludedCol3 = excludedCol2 + ["interactionsAH", "interactionsDO", "c_TD3", "c_TD6"]
modelFull = steplnr.CalculateModel(explo.data[varCol])
xmodel = steplnr.Cross_validation(modelFull.X, modelFull.Y)

savedmodels["R2"] = savedmodels["Features"].apply(xmodel.cross_valide_r2)
savedmodels["MSE"] = savedmodels["Features"].apply(xmodel.cross_valide_mse)
print(savedmodels)

plt.boxplot(savedmodels["R2"])
plt.title("R2")
plt.show()

plt.boxplot(savedmodels["MSE"])
plt.title("MSE")
plt.show()

finalchoice = int(input(f"Based on these metrics, which model would you select ?\n{savedmodels['Model']}. Enter model number:"))
# ## Print final model
fmodel = steplnr.FinalModel(model.X, model.Y, savedmodels.iat[finalchoice, 1])
fmodel.afficheEq()

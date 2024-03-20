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
import EDA
import note, trace, merger, steplnr
import features as ft
import matplotlib.pyplot as plt

## Raw dataset loading
n = note.Note("data/notes_anonymes.csv").data
t = trace.Trace("data/logs_anonymes.csv").data
## Feature extraction from trace
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
explo.boxplot(explo.dataN.loc[:, explo.dataN.columns != 'note'])
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
while colToDelete != "STOP":
      model.calculate()
      colToDelete = input("Quelle variable voulez vous supprimer ? (Pour arrêter entrez STOP) ")
      if colToDelete in model.X:
          model.X = model.X.drop(columns=colToDelete)
## Cross validation
excludedCol1 = excludedCol + ["ev_presence_check", "day_with_inter", "ev_presence_set", "session_sum"]
excludedCol2 = excludedCol1 + ["c_notTD", "c_TD5", "ev_course_access", "c_TD7", "ev_homework_status"]
excludedCol3 = excludedCol2 + ["interactionsAH", "interactionsDO", "c_TD3", "c_TD6"]
xmodel = steplnr.Cross_validation(model.X, model.Y)
scores = xmodel.cross_valide(excludedCol, cv=10)
scores1 = xmodel.cross_valide(excludedCol1, cv=10)
scores2 = xmodel.cross_valide(excludedCol2, cv=10)
scores3 = xmodel.cross_valide(excludedCol3, cv=10)
for s in xmodel.scoring:
     plt.boxplot([scores[f"test_{s}"], scores1[f"test_{s}"], scores2[f"test_{s}"], scores3[f"test_{s}"]],
             labels=["Modèle1", "Modèle2", "Modèle3", "Modèle4"])
     plt.title(f"{s}")
     plt.show()
## Print final model
fmodel = steplnr.FinalModel(model.X, model.Y, excludedCol3)
fmodel.afficheEq()

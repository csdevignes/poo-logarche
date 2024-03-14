'''
Projet final
Analyse des traces de Arche en lien avec les notes des étudiants

@Usage:

@author: Claire-Sophie Devignes
@copyright: Institut des sciences du Digital, Management & Cognition – IDMC
@license: MIT License
@version: 1.0
@email: claire-sophie.devignes9@etu.univ-lorraine.fr
@date: 15 février 24
'''
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import trace, note, features, merger
import numpy as np
from tabulate import tabulate
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from scipy.stats import kstest
from outliers import smirnov_grubbs as grubbs
import math

# Pandas option to be set for optimal data exploration
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', 1000)

class EDA:
    def __init__(self, data):
        '''
        '''
        self.data = pd.DataFrame(data)
        self.removenull()
        self.filterLine("course_access", 75)
        self.filterLine("allTD", 100)
        self.filterLine("user_time", 40)
        self.filterLine("interactionsDO", 25)
        self.normalize(self.data)
        self.logtransformation()
    def removenull(self):
        self.data.fillna(0, inplace=True)
    def normalize(self, data):
        scaler = StandardScaler().fit(data)
        self.dataN = scaler.transform(data)
        self.dataN = pd.DataFrame(self.dataN)
        self.dataN.columns = data.columns
    def logtransformation(self):
        self.dataLog = np.log(self.data + 1)
        self.dataLog["note"] = self.data["note"]
    def outlierGrubbs(self, data, column_name):
        #Test for normality
        normality = kstest(data[column_name], "norm")
        if normality[1] < 0.05:
            print(f"Distribution is not normal for {column_name}. Grubbs aborted.")
        else:
            print(f"{column_name} has a normal distribution. Outliers:")
            idoutliers = grubbs.two_sided_test_indices(data[column_name], alpha=.05)
            valueoutliers = grubbs.two_sided_test_outliers(data[column_name], alpha=.05)
            print(f"Index: {idoutliers}")
            print(f"Values: {valueoutliers}")
    def filterLine(self, feature, threshold, inf=True):
        if inf:
            self.data = self.data.loc[self.data[feature] < threshold]
        else:
            self.data = self.data.loc[self.data[feature] > threshold]
    def boxplot(self, dataplot):
        dataplot.boxplot(grid=False, rot=90)
        plt.show()
    def histoplot(self, dataplot, column="note"):
        dataplot.hist(column=column)
        plt.show()
    def sbpairplot(self, features=[0, 1, 2, 3, 4, 5]):
        sb.pairplot(self.data.iloc[:, features])
        plt.show()
    def sbdisplot(self, features="note"):
        sb.displot(self.data, x=features, hue="note")
        plt.show()
    def correlation(self):
        corr = self.data.corr()
        # Generate a mask for the upper triangle
        mask = np.zeros_like(corr, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        sb.heatmap(corr, annot=True, mask=mask)
        plt.show()

## Outliers

if __name__ == "__main__":
    # Creation of the merged dataset including per user grades and generated features
    n = note.Note("data/notes_anonymes.csv")
    m = merger.Merger(n.data, "feature/").data
    #m.to_csv("merged_dataset.csv")
    explo = EDA(m)
    print(explo.data.shape)
    #print(explo.data.head())
    #explo.sbdisplot("interactions")
    #explo.boxplot(explo.dataN)
    #explo.boxplot(explo.data)
    #explo.correlation()
    #for col in explo.dataN.columns:
    #    explo.outlierGrubbs(explo.dataN, col)
    # Trace import
    t = trace.Trace("data/logs_anonymes.csv").data
    print(t.shape)
    # Liste des étudiants
    etudiants = n.data.index.values
    print(etudiants)
    # Liste des profs
    profs = [x for x in t["Utilisateur"].factorize()[1].values if x not in etudiants]
    print(profs)
    t["Statut"] = t["Utilisateur"].replace(etudiants, "etudiant")
    t["Statut"] = t["Statut"].replace(profs, "prof")
    print(t.shape)
    print(t.loc[t["Composant"] == "Système",["Contexte", "Evenement", "Statut"]].groupby(t["Statut"]).value_counts())

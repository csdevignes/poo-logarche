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
        self.targetCol = ["note", "success", "mention"]
        self.varCol = [col for col in self.data.columns if col not in self.targetCol]
        self.filterLine("comp_devoir", 130)
        self.filterLine("c_TD_all", 100)
        self.filterLine("comp_fichier", 120)
        self.filterLine("comp_systeme", 80)
        self.filterLine("variete_composant", 3, inf=False)
        self.normalize()
        self.logtransformation()
    def removenull(self):
        self.data.fillna(0, inplace=True)
    def normalize(self):
        '''
        Perform a normalisation of non-target variables
        Then add the target variables to dataset
        '''
        scaler = StandardScaler().fit(self.data[self.varCol])
        self.dataN = scaler.transform(self.data[self.varCol])
        self.dataN = pd.DataFrame(self.dataN, index=self.data.index)
        self.dataN.columns = self.data[self.varCol].columns
        self.dataN[self.targetCol] = self.data[self.targetCol]
    def logtransformation(self):
        '''
        Perform a logarithm transformation of non-target variables
        Then add the target variables to dataset
        '''
        self.dataLog = np.log((self.data[self.varCol]) + 1)
        self.dataLog[self.targetCol] = self.data[self.targetCol]
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
        dataplot.plot(kind='box', rot = 90)
        plt.show()
    def histoplot(self, dataplot, column="note"):
        dataplot.hist(column=column)
        plt.show()
    def sbpairplot(self, features=[0, 1, 2, 3, 4, 5]):
        sb.pairplot(self.data.iloc[:, features])
        plt.show()
    def sbdisplot(self, features="note"):
        '''
        Creates a distribution plot from a specific feature of the data
        Plot is colored with target variable
        :param features:
        :return:
        '''
        sb.displot(self.data, x=features, hue="mention")
        plt.show()
    def correlation(self):
        '''
        Creates a correlation plot from the data
        '''
        corr = self.data.corr()
        # Generate a mask for the upper triangle
        mask = np.zeros_like(corr, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        sb.heatmap(corr, annot=True, mask=mask, xticklabels=True, yticklabels=True)
        plt.show()


if __name__ == "__main__":
    # Creation of the merged dataset including per user grades and generated features
    n = note.Note("data/notes_anonymes.csv")
    m = merger.Merger(n.data, "feature/").data
    # m.to_csv("merged_dataset.csv")
    explo = EDA(m)
    print(explo.dataN.shape)
    explo.sbdisplot("ev_homework_handed")
    # explo.boxplot(explo.dataN)
    # explo.correlation()
    #for col in explo.dataN.columns:
    #    explo.outlierGrubbs(explo.dataN, col)

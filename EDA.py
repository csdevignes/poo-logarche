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

class EDA:
    '''
    Object EDA contains all the methods for exploratory data analysis and data cleaning.
    '''
    def __init__(self, data):
        '''
        Loads dataframe from merger and calls all data cleaning methods
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
        '''
        Replaces null values with zeros.
        '''
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
        '''
        Test a specific columns for outlier presence, using Grubbs
        method.
        :param data: normalized dataframe dataN
        :param column_name: name of the feature to test for outliers
        '''
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
        '''
        Allows filtering of the dataset according to
        :param feature: name of feature column to filter on
        :param threshold: numeric value to use for filter
        :param inf: bool, if True keeps values below threshold
                if False keeps values above threshold
        '''
        if inf:
            self.data = self.data.loc[self.data[feature] < threshold]
        else:
            self.data = self.data.loc[self.data[feature] > threshold]
    def boxplot(self, dataplot):
        '''
        Generates boxplot from a specified subset of the data
        :param dataplot: dataframe to plot
        '''
        dataplot.plot(kind='box', rot = 90)
        plt.show()
    def histoplot(self, dataplot, column="note"):
        '''
        Generates simple histoplot to see distribution of a
        feature
        :param dataplot: dataframe
        :param column: string, feature to plot distribution on
        '''
        dataplot.hist(column=column)
        plt.show()
    def sbpairplot(self, features=[0, 1, 2, 3, 4, 5]):
        '''
        Generates a pairplot of features against each other, with
        distribution plot in the diagonal line.
        :param features: list of indices of column features to plot
        '''
        sb.pairplot(self.data.iloc[:, features])
        plt.show()
    def sbdisplot(self, features="note"):
        '''
        Creates a fancy distribution histoplot from a specific
        feature of the data. Plot is colored with target variable
        :param features: string, feature to plot distribution on
        '''
        sb.displot(self.data, x=features, hue="mention")
        plt.show()
    def correlation(self, excludedCol = None):
        '''
        Creates a correlation plot from the data
        :param excludedCol: list of column names to exclude
        '''
        varCol = [col for col in self.data.columns if col not in excludedCol]
        corr = self.data[varCol].corr()
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
    excludedCol = ["success", "mention", "comp_devoir", "comp_fichier", "comp_feedback", "comp_presence",
                   "comp_remises", "comp_systeme", "c_TD_all", "interactions", "ev_class_access"]
    explo.correlation(excludedCol)
    #for col in explo.dataN.columns:
    #    explo.outlierGrubbs(explo.dataN, col)

'''
Projet final
Analyse des traces de Arche en lien avec les notes des étudiants
Machine learning - linear regression

@Usage:

@author: Claire-Sophie Devignes
@copyright: Institut des sciences du Digital, Management & Cognition – IDMC
@license: MIT License
@version: 1.0
@email: claire-sophie.devignes9@etu.univ-lorraine.fr
@date: 22 février 24
'''

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
from tabulate import tabulate
import note, merger, EDA

# We define the functions for calculation of linear model using statsmodel and scikit-learn packages
def calculSM(X, Y) :
     """
     Modélisation des données avec statsmodels: permet d'obtenir le AIC et les p-values
     :param X: données explicatives, tableau pandas
     :param Y: donnée à expliquer, tableau pandas
     :return: l'objet statsmodels resultatSM qui contient les résultats de la régression lineaire
     """
     #On rajoute la constante a X pour avoir le beta 0, la colonne est automatiquement appelée const
     #Xconst = sm.add_constant(X)
     #On crée le modèle et utilise la méthode fit pour trouver l'estimation des coefficients
     lnrSM = sm.OLS(Y,X, hasconst=True)
     resultatSM = lnrSM.fit(disp=0) #On met disp=0 pour éviter qu'il affiche des messages à chaque calcul
     return resultatSM

class LinearSK:
    def __init__(self, X, Y, cv=10):
        self.X = X
        self.Y = Y
        self.cv = cv
        self.calculatelnr()
        self.calculateMSE()
    def calculatelnr(self):
        regR = LinearRegression()
        regR.fit(self.X, self.Y)
        #scores = cross_val_score(regR, X, Y, cv=cv, scoring='accuracy')
        self.r2score = regR.score(self.X, self.Y)
        self.predictions = regR.predict(self.X)
    def calculateMSE(self):
        self.mse = mean_squared_error(self.Y, self.predictions)

class CalculateModel:
    def __init__(self, data):
        '''
        Collect input dataframe, split it, calculate linear models
        and print a pretty table with all the indicators calculated.
        :param data: dataframe
        '''
        self.data = pd.DataFrame(data)
        self.split()
    def split(self):
        self.X = self.data.loc[:, self.data.columns != "note"]
        self.Y = self.data["note"]
    def calculate(self):
        '''
        This function calculates full linear regression model, using methods from:
        - statmodels to obtain coefficients, p-values and aic
        - scikit learn to obtain r2score and mean square error
        It then calls calculatesubs() method in order to repeat model calculation
        when removing one of the features.
        Current model R², AIC and MSE are printed while p-values and coefficients are
        stored in resDF dataframe.
        '''
        resSM = calculSM(self.X, self.Y)
        self.resDF = pd.DataFrame(index=resSM.params.index)
        self.resDF["Coef"] = resSM.params
        self.resDF["Pvalues"] = resSM.pvalues
        resSK = LinearSK(self.X, self.Y)
        print(f'Current Model: R²: {resSK.r2score}, AIC : {resSM.aic}, MSE : {resSK.mse}')
        self.calculatesubs()
    def calculatesubs(self):
        '''
        Calculate linear model for each new set of features X that
        can be obtained by removing one of the features.
        Append indicators results into resDF dataframe.
        '''
        for col in self.X.columns:
            newX = self.X.drop(columns=col)
            scoresNewX = LinearSK(newX, self.Y)
            resultatNewX = calculSM(newX, self.Y)
            self.resDF.loc[col, "AIC"] = resultatNewX.aic
            self.resDF.loc[col, "R²"] = scoresNewX.r2score
            self.resDF.loc[col, "MSE"] = scoresNewX.mse
        print(tabulate(self.resDF, headers="keys", tablefmt="psql", floatfmt=".3f"))


if __name__ == "__main__":
    n = note.Note("data/notes_anonymes.csv")
    merged = merger.Merger(n.data,"feature/").data
    explo = EDA.EDA(merged)
    print(explo.data)
    colToDelete = ""
    # excludedCol = ["success", "mention"]
    excludedCol = ["success", "mention", "comp_devoir", "comp_fichier", "comp_feedback", "comp_presence", "comp_remises", "comp_systeme", "c_TD_all", "interactions", "ev_class_access"]
    varCol = [col for col in explo.data.columns if col not in excludedCol]
    model = CalculateModel(explo.data[varCol])
    while colToDelete != "STOP":
         model.calculate()
         colToDelete = input("Quelle variable voulez vous supprimer ? (Pour arrêter entrez STOP) ")
         if colToDelete in model.X:
             model.X = model.X.drop(columns=colToDelete)

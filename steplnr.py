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
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.metrics import mean_squared_error
from tabulate import tabulate
import note, merger, EDA

def calculSM(X, Y) :
     """
     Data modelisation using statsmodels: allows to obtain the coefficients, AIC and p-values
     :param X: dataframe with all the created features
     :param Y: dataframe with target feature
     :return: A statsmodels object which contains resutls of linear regression
     """
     lnrSM = sm.OLS(Y,X, hasconst=True)
     resultatSM = lnrSM.fit(disp=0)
     return resultatSM

class LinearSK:
    '''
    Object LinearSK which calculates r2 score and mean squared error
    for a given X and Y
    '''
    def __init__(self, X, Y):
        '''
        Initialize LinearSK object using
        :param X: dataframe with all created features
        :param Y: dataframe with target feature
        '''
        self.X = X
        self.Y = Y
        self.calculatelnr()
        self.calculateMSE()
    def calculatelnr(self):
        '''
        Compute linear regression and store score and prediction
        '''
        regR = LinearRegression()
        regR.fit(self.X, self.Y)
        self.r2score = regR.score(self.X, self.Y)
        self.predictions = regR.predict(self.X)
    def calculateMSE(self):
        '''
        Calculates mean squared error
        '''
        self.mse = mean_squared_error(self.Y, self.predictions)

class CalculateModel:
    '''
    Object regrouping data loading and linear regression methods
    as well as result display
    '''
    def __init__(self, data):
        '''
        Collect input dataframe and split it
        :param data: dataframe from EDA
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
class Cross_validation:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
    def cross_valide_r2(self, varCol, cv=5):
        self.scoring = ['r2', 'neg_mean_squared_error']
        varCol = varCol
        regR = LinearRegression()
        self.scores = cross_validate(regR, self.X[varCol], self.Y, cv=cv, scoring=self.scoring)
        return self.scores["test_r2"]
    def cross_valide_mse(self, varCol, cv=5):
        self.scoring = ['r2', 'neg_mean_squared_error']
        varCol = varCol
        regR = LinearRegression()
        self.scores = cross_validate(regR, self.X[varCol], self.Y, cv=cv, scoring=self.scoring)
        return self.scores["test_neg_mean_squared_error"]
class FinalModel:
    def __init__(self, X, Y, varCol):
        self.X = X
        self.Y = Y
        self.X = self.X[varCol]
    def afficheEq(self):
        resSM = calculSM(self.X, self.Y)
        for index in resSM.params.index:
             print(f"({round(resSM.params[index], 3)} * {index}) + ", end="")


if __name__ == "__main__":
    n = note.Note("data/notes_anonymes.csv")
    merged = merger.Merger(n.data,"feature/").data
    explo = EDA.EDA(merged)
    colToDelete = ""
    # excludedCol = ["success", "mention"]
    # Columns excluded because of high correlaction with other features
    excludedCol = ["success", "mention", "comp_devoir", "comp_fichier", "comp_feedback", "comp_presence", "comp_remises", "comp_systeme", "c_TD_all", "interactions", "ev_class_access"]
    varCol = [col for col in explo.data.columns if col not in excludedCol]
    model = CalculateModel(explo.data[varCol])
    ## Backward selection of the model
    # while colToDelete != "STOP":
    #      model.calculate()
    #      colToDelete = input("Quelle variable voulez vous supprimer ? (Pour arrêter entrez STOP) ")
    #      if colToDelete in model.X:
    #          model.X = model.X.drop(columns=colToDelete)
    ## Cross validation
    excludedCol1 = excludedCol + ["ev_presence_check", "day_with_inter", "ev_presence_set", "session_sum"]
    excludedCol2 = excludedCol1 + ["c_notTD", "c_TD5", "ev_course_access", "c_TD7", "ev_homework_status"]
    excludedCol3 = excludedCol2 + ["interactionsAH", "interactionsDO", "c_TD3", "c_TD6"]
    # xmodel = Cross_validation(model.X, model.Y)
    # scores = xmodel.cross_valide(excludedCol, cv=10)
    # scores1 = xmodel.cross_valide(excludedCol1, cv=10)
    # scores2 = xmodel.cross_valide(excludedCol2, cv=10)
    # scores3 = xmodel.cross_valide(excludedCol3, cv=10)
    # for s in xmodel.scoring:
    #     plt.boxplot([scores[f"test_{s}"], scores1[f"test_{s}"], scores2[f"test_{s}"], scores3[f"test_{s}"]],
    #             labels=["Modèle1", "Modèle2", "Modèle3", "Modèle4"])
    #     plt.title(f"{s}")
    #     plt.show()
    ## Print final model
    fmodel = FinalModel(model.X, model.Y, excludedCol3)
    fmodel.afficheEq()
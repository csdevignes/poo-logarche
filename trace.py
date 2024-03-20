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
import datetime

import pandas as pd
import numpy as np
import locale

class Trace:
    '''
    Creates an object Trace which purpose is to load the log file
    from ARCHE, and preformat its content for further use.
    '''
    def __init__(self, filename):
        '''
        Initialise trace object using several methods called in lire
        :param filename: path to the log file from ARCHE csv file
        '''
        self.lire(filename)
    def lire(self, filename):
        '''
        Read the csv file containing logs from arche in a pandas Dataframe.
        Store it in the data parameter of Trace object.
        :param filename: path to the log file from ARCHE csv file
        '''
        self.data = pd.read_csv(filename)
        self._homogene_dates()
        self._date_formatISO()
        self._rename_columns()
        self._correct_typing()
    def _homogene_dates(self):
        '''
        Convert the dates to a format appropriate with ISO transformation
        Apply a function cell-wise in a column
        '''
        self.data['Heure'] = self.data['Heure'].apply(self._remplace_month)
    def _remplace_month(self, cellule):
        '''
        Replace abbreviated month with full-length month
        :param cellule: cell provided by the apply method from pandas
        '''
        c = cellule.replace("janv.", "janvier") \
        .replace("déc.", "décembre") \
        .replace("nov.", "novembre") \
        .replace("oct.", "octobre") \
        .replace("sept.", "septembre") \
        .replace("juil.", "juillet") \
        .replace("avr.", "avril")
        return c
    def _date_formatISO(self):
        '''
        Convert timestamp to ISO format usable for further calculations
        '''
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        self.data['Heure'] = pd.to_datetime(self.data['Heure'], format="%d %B %y, %H:%M:%S")
    def _rename_columns(self):
        '''
        Changes columns name to make further data manipulation easier
        '''
        self.data = self.data.rename({"Nom complet de l'utilisateur":"Utilisateur", \
                          "Contexte de l'événement":"Contexte", \
                          "Nom de l'événement":"Evenement"}, axis=1)
    def _correct_typing(self):
        '''
        Updating column types from object to string.
        '''
        self.data["Contexte"] = self.data["Contexte"].astype('string')
        self.data["Composant"] = self.data["Composant"].astype('string')
        self.data["Evenement"] = self.data["Evenement"].astype('string')

#Test
if __name__ == "__main__":
    t = Trace("data/logs_anonymes.csv")
    pd.set_option('display.max_columns', None)
    print(t.data.info())
    print(t.data.describe(include="all"))
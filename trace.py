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

#Objet traces: lis le fichier et le met dans un dataframe
#qui est un attribut de l'objet
#Homogénéise les dates
#Apply dans data frame: prend chaque cellule du dataframe et applique la méthode
#donnée en paramètre.
#Change la date en iso
#Enregistre le csv

class Trace:
    '''
    Crée un objet Trace qui sert à charger le fichier log de ARCHE
    Et a remplacer les dates par un objet datetime au format ISO,
    Les séparer dans une nouvelle colonne date
    Ajout d'une colonne TD avec le numero du TD
    '''
    def __init__(self, filename):
        self.lire(filename)
    def lire(self, filename):
        self.data = pd.read_csv(filename)
        self._homogene_dates()
        self._date_formatISO()
        self._rename_columns()
        self._correct_typing()
    def split_date(self):
        self.data["Date"] = pd.to_datetime(self.data["Heure"]).dt.date
    def _homogene_dates(self):
        self.data['Heure'] = self.data['Heure'].apply(self._remplace_month)
    def _remplace_month(self, cellule):
        c = cellule.replace("janv.", "janvier") \
        .replace("déc.", "décembre") \
        .replace("nov.", "novembre") \
        .replace("oct.", "octobre") \
        .replace("sept.", "septembre") \
        .replace("juil.", "juillet") \
        .replace("avr.", "avril")
        return c
    def _date_formatISO(self):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        self.data['Heure'] = pd.to_datetime(self.data['Heure'], format="%d %B %y, %H:%M:%S")
    def _rename_columns(self):
        self.data = self.data.rename({"Nom complet de l'utilisateur":"Utilisateur", \
                          "Contexte de l'événement":"Contexte", \
                          "Nom de l'événement":"Evenement"}, axis=1)
    def _correct_typing(self):
        self.data["Contexte"] = self.data["Contexte"].astype('string')
        self.data["Composant"] = self.data["Composant"].astype('string')
        self.data["Evenement"] = self.data["Evenement"].astype('string')

#Test
if __name__ == "__main__":
    t = Trace("data/logs_anonymes.csv")
    pd.set_option('display.max_columns', None)
    print(t.data.info())
    print(t.data.describe(include="all"))
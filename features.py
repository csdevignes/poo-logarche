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

import trace, note
import pandas as pd
from datetime import datetime, date, time, timedelta
import re
import statistics as stat


class Feature:
    '''
    Crée un objet feature qui extrait les données de trace, crée les catégories nécessaires
    et sauvegarde un fichier .csv
    '''

    def __init__(self, df):
        self.data = df
        self.split_date()
        self.split_hour()
        self.extract_td()

    def split_date(self):
        self.data["Date"] = pd.to_datetime(self.data["Heure"]).dt.date
        self.data["Working_day"] = ((self.data["Date"].between(date(2023, 12, 18), date(2023, 12, 22))) |
                                    (self.data["Date"].between(date(2023, 12, 11), date(2023, 12, 15))) |
                                    (self.data["Date"].between(date(2023, 12, 4), date(2023, 12, 8))) |
                                    (self.data["Date"].between(date(2023, 11, 27), date(2023, 12, 1))) |
                                    (self.data["Date"].between(date(2023, 11, 20), date(2023, 11, 24))) |
                                    (self.data["Date"].between(date(2023, 11, 13), date(2023, 11, 17))) |
                                    (self.data["Date"].between(date(2023, 11, 6), date(2023, 11, 10))) |
                                    (self.data["Date"].between(date(2023, 11, 2), date(2023, 11, 3))))

    def split_hour(self):
        self.data["Hour_only"] = pd.to_datetime(self.data["Heure"]).dt.time
        self.data["Working_hour"] = ((self.data["Hour_only"].between(time(9, 00), time(18, 00))) &
                                     (self.data["Working_day"] == True))

    def extract_td(self):
        self.data["TD"] = self.data["Contexte"].str.extract(r'TD#?(\d)')
        self.data["TD"] = self.data["TD"].astype('object').fillna(0).astype('int64')

    def transformation(self):
        self.feature = self.data

    def save_csv(self, filename="feature"):
        self.feature.to_csv(f"feature/f_{filename}.csv")

class Interactions(Feature):
    '''
    Crée les features Interactions qui correspond au nombre d'interaction par Utilisateur sur toute la période,
    ou seulement en dehors des heures de cours, ou pendant les weekend/vacances.
    '''

    def count_interaction(self):
        self.feature = self.data["Utilisateur"].value_counts()
        self.save_csv("interactions")

    def count_afterhour_interaction(self):
        self.feature = self.data.loc[
            ((self.data["Working_hour"] == False) & (self.data["Working_day"] == True)), "Utilisateur"].value_counts()
        self.save_csv("interactionsAH")

    def count_dayoff_interaction(self):
        self.feature = self.data.loc[(self.data["Working_day"] == False), "Utilisateur"].value_counts()
        self.save_csv("interactionsDO")

    def _count_workhour_interaction(self):
        self.feature = self.data.loc[(self.data["Working_hour"] == True), "Utilisateur"].value_counts()
        self.save_csv("interactionsWH")
    def variete(self):
        col_var = list(("Composant", "Contexte", "Evenement"))
        for col in col_var:
            self.feature = self.data[["Utilisateur", col]].groupby("Utilisateur").nunique()
            self.save_csv(f"variete_{col.lower()}")
        # Recording all different combinations of "Composant", "Contexte", "Evenement"
        self.data["Concat_Var"] = self.data["Composant"].str.cat(self.data[["Contexte", "Evenement"]], na_rep="-")
        self.feature = (self.data[["Utilisateur", "Concat_Var"]]
                        .groupby("Utilisateur").nunique())
        self.save_csv("variete_all")
    def day_with_inter(self):
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").nunique()
        self.save_csv("day_with_inter")
    def inter_per_day_mean(self):
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").value_counts()
        self.feature = self.feature.groupby("Utilisateur").mean()
        self.save_csv("inter_per_day_mean")
    def inter_per_day_var(self):
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").value_counts()
        self.feature = self.feature.groupby("Utilisateur").var()
        self.save_csv("inter_per_day_var")
class InteractionType(Feature):
    '''
    Crée les feature Study qui tentent de caractériser les type d'interactions des étudiants avec ARCHE
    quantifie la présence effective en cours, la consultation des rapports de présence, l'accès à la page d'accueil du cours,

    '''
    def composant(self):
        self.composants = self.data["Composant"].value_counts()
        self.composants = self.composants.loc[self.composants.values > 100].index
        for comp in self.composants:
            self.feature = self.data.loc[(self.data["Composant"] == comp), "Utilisateur"].value_counts()
            self.save_csv(f"comp_{re.sub('[éè]', 'e', comp.split()[0].lower())}")
    def evenements(self):
        self.evenement_list = {"Statut de présence renseigné par l'étudiant": "presence_set",
                           "Rapport de session consulté": "presence_check",
                           "Cours consulté": "class_access",
                           "Fichier déposé": "homework_handed",
                           "Statut du travail remis consulté": "homework_status",
                            "Module de cours consulté": "course_access"
                           }
        for ev in self.evenement_list:
            self.feature = self.data.loc[(self.data["Evenement"] == ev), "Utilisateur"].value_counts()
            self.save_csv(f"ev_{self.evenement_list[ev]}")
class Materials(Feature):
    '''
    Crée les feature Materials, qui définissent comment les étudiants interagissent avec les fichiers sur Arche
    quantifie le nombre de fichier déposé pour les devoirs, le nombre de consultation de chaque TD
    et du reste des cours.
    '''
    def td(self):
        for i in range(1, 8):
            if i > 0:
                self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
                            self.data["TD"] == i)), "Utilisateur"].value_counts()
                self.save_csv(f"c_TD{i}")

    def alltd(self):
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
            self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("c_TD_all")

    def course_access(self):
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
            ~self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("c_notTD")
class UserTime(Feature):
    def session_time_record(self):
        self.data = self.data.sort_values(by=["Utilisateur", "Heure"], axis=0)
        self.res = dict()
        user = self.data.iat[0, 1]
        temps = self.data.iat[0, 0]
        duree = timedelta(seconds=1)
        for index, ligne in self.data.iterrows():
            if ligne["Utilisateur"] == user and abs(ligne["Heure"] - temps) <= timedelta(minutes=5):
                #If user is the same and time difference < 5 min
                duree = duree + abs(ligne["Heure"] - temps)
            else:
                if user in self.res.keys():
                    self.res[user].append(duree.total_seconds())
                else:
                    self.res[user] = [duree.total_seconds()]
                duree = timedelta(seconds=1)
            user = ligne["Utilisateur"]
            temps = ligne["Heure"]
    def session_sum(self):
        resSum = self.res.copy()
        for x, y in resSum.items():
            resSum[x] = sum(y) /60
        self.feature = pd.Series(resSum)
        self.feature.index.name = "Utilisateur"
        self.save_csv("session_sum")
    def session_avg(self):
        resAvg = self.res.copy()
        for x, y in resAvg.items():
            resAvg[x] = stat.mean(y) /60
        self.feature = pd.Series(resAvg)
        self.feature.index.name = "Utilisateur"
        self.save_csv("session_avg")

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    t = trace.Trace("data/logs_anonymes.csv").data
    f_inter = Interactions(t)
    f_inter.inter_per_day_mean()
    f_inter.inter_per_day_var()
    # f_inter.variete()
    # f_inter.count_afterhour_interaction()
    # f_inter.count_dayoff_interaction()
    # f_inter.count_interaction()
    # f_type = InteractionType(t)
    # f_type.evenements()
    # # f_type.composant()
    # f_mat = Materials(t)
    # # # f_mat.td()
    # f_mat.alltd()
    # f_mat.course_access()
    # f_time = UserTime(t)
    # f_time.session_time_record()
    # f_time.session_sum()
    # f_time.session_avg()
    pd.options.display.max_rows = 999
    print(f_inter.feature.head())

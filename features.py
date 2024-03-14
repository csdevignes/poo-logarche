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

import trace, note
import pandas as pd
from datetime import datetime, date, time, timedelta
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
                                    (self.data["Date"].between(date(2023, 11, 2), date(2023, 11, 3))) )
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
        self.feature.to_csv(f"feature/{filename}.csv")
class Interactions(Feature):
    '''
    Crée les features Interactions qui correspond au nombre d'interaction par Utilisateur sur toute la période,
    ou seulement en dehors des heures de cours, ou pendant les weekend/vacances.
    '''
    def count_interaction(self):
        self.feature = self.data["Utilisateur"].value_counts()
        self.save_csv("f_interactions")
    def count_afterhour_interaction(self):
        self.feature = self.data.loc[((self.data["Working_hour"] == False) & (self.data["Working_day"] == True)), "Utilisateur"].value_counts()
        self.save_csv("f_interactionsAH")
    def count_dayoff_interaction(self):
        self.feature = self.data.loc[(self.data["Working_day"] == False), "Utilisateur"].value_counts()
        self.save_csv("f_interactionsDO")
    def _count_workhour_interaction(self):
        self.feature = self.data.loc[(self.data["Working_hour"] == True), "Utilisateur"].value_counts()
        self.save_csv("f_interactionsWH")

class Study(Feature):
    '''
    Crée les feature Study qui tentent de caractériser les type d'interactions des étudiants avec ARCHE
    quantifie la présence effective en cours, la consultation des rapports de présence, l'accès à la page d'accueil du cours,

    '''
    def presence(self):
        self.feature = self.data.loc[(self.data["Evenement"] == "Statut de présence renseigné par l'étudiant"), "Utilisateur"].value_counts()
        self.save_csv("f_presence")
    def presence_check(self):
        self.feature = self.data.loc[(self.data["Evenement"] == "Rapport de session consulté"), "Utilisateur"].value_counts()
        self.save_csv("f_presencecheck")
    def class_access(self):
        self.feature = self.data.loc[(self.data["Evenement"] == "Cours consulté"), "Utilisateur"].value_counts()
        self.save_csv("f_classaccess")
class Materials(Feature):
    '''
    Crée les feature Materials, qui définissent comment les étudiants interagissent avec les fichiers sur Arche
    quantifie le nombre de fichier déposé pour les devoirs, le nombre de consultation de chaque TD
    et du reste des cours.
    '''
    def homework(self):
        self.feature = self.data.loc[(self.data["Evenement"] == "Fichier déposé"), "Utilisateur"].value_counts()
        self.save_csv("f_homework")
    def td(self):
        for i in range(1,8):
            if i > 0:
                self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (self.data["TD"] == i)), "Utilisateur"].value_counts()
                self.save_csv(f"f_TD{i}")
    def alltd(self):
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("f_allTD")
    def course_access(self):
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (~self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("f_course_access")
class UserTime(Feature):
    def user_time(self):
        self.feature = pd.DataFrame(columns=["Utilisateur", "Durée"])
        user = self.data.iat[0, 1]
        temps = self.data.iat[0, 0]
        duree = timedelta(seconds=1)
        for index, ligne in self.data.iterrows():
            if ligne["Utilisateur"] != user:
                if user in self.feature["Utilisateur"].values:
                    self.feature.loc[self.feature["Utilisateur"] == user, "Durée"] = self.feature.loc[self.feature["Utilisateur"] == user, "Durée"] + (duree.total_seconds() / 60)
                else:
                    self.feature.loc[len(self.feature)] = [user, (duree.total_seconds() / 60)]
                duree = timedelta(seconds=1)
            elif ligne["Utilisateur"] == user and abs(ligne["Heure"] - temps) <= timedelta(minutes=5):
                duree = duree + abs(ligne["Heure"] - temps)
            user = ligne["Utilisateur"]
            temps = ligne["Heure"]
            print(temps)
        self.feature.set_index("Utilisateur", inplace=True)
        self.save_csv("f_user_time")

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    t = trace.Trace("data/logs_anonymes.csv").data
    # f_inter = Interactions(t)
    # f_inter.count_interaction()
    # f_inter.count_dayoff_interaction()
    # f_inter.count_afterhour_interaction()
    # f_study = Study(t)
    # f_study.class_access()
    # f_study.presence_check()
    # f_study.presence()
    f_mater = Materials(t)
    f_mater.alltd()
    # f_mater.homework()
    # f_mater.td()
    # f_mater.course_access()
    #f_time = UserTime(t)
    #f_time.user_time()



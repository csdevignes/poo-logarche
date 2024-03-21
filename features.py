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
    Create a general object Feature which extract data from trace, creates neeeded
    categories and save a .csv file
    '''

    def __init__(self, df):
        '''
        Initialize object with dataframe obtained from trace object
        :param df: dataframe from trace
        '''
        self.data = df
        self.split_date()
        self.split_hour()
        self.extract_td()

    def split_date(self):
        '''
        Creates a column date from "Heure". Categorizes date in working days
        (1) and off-days (0).
        '''
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
        '''
        Creates a column "hour only" from "Heure". Categorizes data in working
        hours (1) and off-hours (0).
        '''
        self.data["Hour_only"] = pd.to_datetime(self.data["Heure"]).dt.time
        self.data["Working_hour"] = ((self.data["Hour_only"].between(time(9, 00), time(18, 00))) &
                                     (self.data["Working_day"] == True))
    def extract_td(self):
        '''
        Creates a column "TD" which contains the number of the TD to which
        the log entry is related.
        '''
        self.data["TD"] = self.data["Contexte"].str.extract(r'TD#?(\d)')
        self.data["TD"] = self.data["TD"].astype('object').fillna(0).astype('int64')
    def save_csv(self, filename="feature"):
        '''
        Creates a method to save a given feature as csv, in the feature
        folder.
        :param filename: string, name of the feature to be saved
        '''
        self.feature.to_csv(f"feature/f_{filename}.csv")

class Interactions(Feature):
    '''
    Creates the features Interactions which are related to the count of
    interaction per user, their frequency and variety.
    '''

    def count_interaction(self):
        '''
        Count the total number of interactions per user.
        '''
        self.feature = self.data["Utilisateur"].value_counts()
        self.save_csv("interactions")
        print("All interactions : interactions")

    def count_afterhour_interaction(self):
        '''
        Count the number of interaction on off-hours, on working days.
        '''
        self.feature = self.data.loc[
            ((self.data["Working_hour"] == False) & (self.data["Working_day"] == True)), "Utilisateur"].value_counts()
        self.save_csv("interactionsAH")
        print("After-hour interactions : interactionsAH")

    def count_dayoff_interaction(self):
        '''
        Count the number of interaction on off-days.
        '''
        self.feature = self.data.loc[(self.data["Working_day"] == False), "Utilisateur"].value_counts()
        self.save_csv("interactionsDO")
        print("Day-off interactions : interactionsDO")

    def _count_workhour_interaction(self):
        '''
        Count the number of interaction on working-hours, used for control of the methods only.
        '''
        self.feature = self.data.loc[(self.data["Working_hour"] == True), "Utilisateur"].value_counts()
        self.save_csv("interactionsWH")
    def variete(self):
        '''
        Count the variety of interactions, as the number of different interaction per student.
        Summarize the number of distinct interactions.
        Quantified for each column individually and then for the combination of the 3 columns.
        '''
        col_var = list(("Composant", "Contexte", "Evenement"))
        for col in col_var:
            self.feature = self.data[["Utilisateur", col]].groupby("Utilisateur").nunique()
            self.save_csv(f"variete_{col.lower()}")
        # Recording all different combinations of "Composant", "Contexte", "Evenement"
        self.data["Concat_Var"] = self.data["Composant"].str.cat(self.data[["Contexte", "Evenement"]], na_rep="-")
        self.feature = (self.data[["Utilisateur", "Concat_Var"]]
                        .groupby("Utilisateur").nunique())
        self.save_csv("variete_all")
        print("Interaction variety : variete_[...]")
    def day_with_inter(self):
        '''
        Count the number of day with at least one interaction per user.
        '''
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").nunique()
        self.save_csv("day_with_inter")
        print("Day with interaction : day_with_inter")
    def inter_per_day_mean(self):
        '''
        Count the number of interaction per day, and aggregates the mean.
        '''
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").value_counts()
        self.feature = self.feature.groupby("Utilisateur").mean()
        self.save_csv("inter_per_day_mean")
        print("Mean interactions per day : inter_per_day_mean")
    def inter_per_day_var(self):
        '''
        Count the number of interaction per day, and aggregates the variance.
        '''
        self.feature = self.data.loc[:, ["Utilisateur", "Date"]].groupby("Utilisateur").value_counts()
        self.feature = self.feature.groupby("Utilisateur").var()
        self.save_csv("inter_per_day_var")
        print("Variance of interactions per day : inter_per_day_var")
class InteractionType(Feature):
    '''
    Creates the features describing the type of interaction of students.
    '''
    def composant(self):
        '''
        Count the number of interactions related to each "Composant"
        '''
        self.composants = self.data["Composant"].value_counts()
        self.composants = self.composants.loc[self.composants.values > 100].index
        for comp in self.composants:
            self.feature = self.data.loc[(self.data["Composant"] == comp), "Utilisateur"].value_counts()
            self.save_csv(f"comp_{re.sub('[éè]', 'e', comp.split()[0].lower())}")
        print("Interaction related to each composant : comp_[...]")
    def evenements(self):
        '''
        Count the number of interactions related to each "Evenement",
        selected previously from trace data analysis.
        '''
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
        print(f"Events : {self.evenement_list}")
class Materials(Feature):
    '''
    Creates the features Materials describing interactions of students with files available on Arche.
    '''
    def td(self):
        '''
        Count the amount of events related to each TD
        '''
        for i in range(1, 8):
            if i > 0:
                self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
                            self.data["TD"] == i)), "Utilisateur"].value_counts()
                self.save_csv(f"c_TD{i}")
        print("Interaction with TD Materials : c_TD1, ..., c_TD7")
    def alltd(self):
        '''
        Count the amount of events related to any TD
        '''
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
            self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("c_TD_all")
        print("Interaction with any TD Materials : c_TD_all")

    def course_access(self):
        '''
        Count the amount of events of course consultation not related to any TD
        '''
        self.feature = self.data.loc[((self.data["Evenement"] == "Module de cours consulté") & (
            ~self.data["TD"].isin([1, 2, 3, 4, 5, 6, 7]))), "Utilisateur"].value_counts()
        self.save_csv("c_notTD")
        print("Interaction with non-TD Materials : c_notTD")
class UserTime(Feature):
    '''
    Creates the features UserTime related to user session duration
    '''
    def session_time_record(self):
        '''
        Quantifies the duration of each session. Session ends when user stay inactive
        for more than 5 min. Stores information for each session in a dict
        user : [list of session durations]
        '''
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
        '''
        Quantifies the total time spent on arche per user
        '''
        resSum = self.res.copy()
        for x, y in resSum.items():
            resSum[x] = sum(y) /60
        self.feature = pd.Series(resSum)
        self.feature.index.name = "Utilisateur"
        self.save_csv("session_sum")
        print("Total time spent online : session_sum")
    def session_avg(self):
        '''
        Quantifies the average session time per user
        '''
        resAvg = self.res.copy()
        for x, y in resAvg.items():
            resAvg[x] = stat.mean(y) /60
        self.feature = pd.Series(resAvg)
        self.feature.index.name = "Utilisateur"
        self.save_csv("session_avg")
        print("Average session duration : session_avg")

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

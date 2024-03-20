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
import pandas as pd

class Note:
    '''
    Creates a Note object to load grade data from a csv file
    and pre-format it for further analyses.
    '''
    def __init__(self, filename):
        '''
        Initialize Note object by reading and processing the file
        :param filename: path to grade csv file
        '''
        self.lire(filename)
        self.grade_category()
    def lire(self, filename):
        '''
        Read the csv setting "ID" as index column, and call processing methods
        :param filename: path to grade csv file
        '''
        self.data = pd.read_csv(filename, index_col="ID")
        self._remove_absents()
        self._correct_typing()
    def _remove_absents(self):
        '''
        Remove lines with no grade (absent students)
        '''
        self.data = self.data[self.data["note"] != "ABS"]
    def _correct_typing(self):
        '''
        Set the proper type for grades
        '''
        self.data["note"] = self.data["note"].astype('float')
    def grade_category(self):
        '''
        Creates categorical variables from notes
        '''
        self.data['success'] = self.data.apply(lambda row: self._success(row['note']), axis=1)
        self.data['mention'] = self.data.apply(lambda row: self._mention(row['note']), axis=1)
    def _success(self, x):
        '''
        Define lambda function to use for categorical variable creation
        :param x: grade column
        :return: 0 if grade < 10, else 1
        '''
        if x < 10:
            return '0'
        else:
            return '1'
    def _mention(self, x):
        '''
        Define lambda function to use for categorical variable creation
        :param x: grade column
        :return: 0 if grade < 10, 1 if < 12, 2 if < 14, 3 if < 16, 4 if < 18, else 5
        '''
        if x < 10:
            return '0'
        elif x < 12:
            return '1'
        elif x < 14:
            return '2'
        elif x < 16:
            return "3"
        elif x < 18:
            return '4'
        else:
            return '5'

if __name__ == "__main__":
    n = Note("data/notes_anonymes.csv")
    print(n.data)
    n.data["success"].value_counts().hist()
    plt.show()
    print(n.data["success"].value_counts())
    print(n.data["mention"].value_counts())
    n.data["mention"].value_counts().hist()
    plt.show()

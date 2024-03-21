'''
Projet final
Analyse des traces de Arche en lien avec les notes des étudiants

@Usage:

@author: Claire-Sophie Devignes
@copyright: Institut des sciences du Digital, Management & Cognition – IDMC
@license: MIT License
@version: 1.0
@email: claire-sophie.devignes9@etu.univ-lorraine.fr
@date: 22 février 24
'''

import pandas as pd
import trace, note
import os

class Merger:
    '''
    Create a Merger object, which will create a dataframe from the grade
    dataframe previously created, together with all the feature csv files
    previously stored in a specified folder. Needed arguments:
    gradedf: dataframe containing grades for each id
    dirpath: path of directory containing the feature csv files
    '''
    def __init__(self, gradedf, dirpath):
        self.data = pd.DataFrame(gradedf)
        for filename in os.listdir(dirpath):
            if filename.endswith('.csv') and filename.startswith('f_'):
                self.merge(f'{dirpath}{filename}')
            else:
                continue
        print("Dataset merged.")
    def merge(self, featurefile):
        '''
        Merge one feature with the grade dataframe
        :param featurefile: path of the .csv feature file
        '''
        self.feature1 = pd.read_csv(featurefile, index_col="Utilisateur")
        # Generating a name for the feature column in the dataframe
        featurename = featurefile[10:-4]
        #Adding the new feature in the dataframe
        self.data[featurename] = self.feature1

#test
if __name__ == "__main__":
    n = note.Note("data/notes_anonymes.csv")
    m = Merger(n.data,"feature/")
    print(m.data.head())
    print(m.data.shape)



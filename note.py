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

import pandas as pd

# Charge le fichier csv des notes
# Et supprime les étudiants absents

class Note:
    '''
    Crée un objet Note qui sert à charger le fichier notes
    Et a supprimer les élèves absents
    '''
    def __init__(self, filename):
        self.lire(filename)
    def lire(self, filename):
        self.data = pd.read_csv(filename, index_col="ID")
        self._remove_absents()
        self._correct_typing()
    def _remove_absents(self):
        self.data = self.data[self.data["note"] != "ABS"]
    def _correct_typing(self):
        self.data["note"] = self.data["note"].astype('float')

if __name__ == "__main__":
    n = Note("data/notes_anonymes.csv")
    print(n.data.index.sort_values())

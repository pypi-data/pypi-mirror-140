import pandas as pd
from pathlib import Path

default_mass_list = f'{str(Path(__file__).parents[0])}/mass_list.xlsx'

def load_mass_list(filename=default_mass_list):
    df = pd.read_excel(filename)
    mass_list = {}
    for index, row in df.iterrows():
        mass_list[str(row['dp'])] = [row['low'], row['high']]
    return mass_list

if __name__ =='__main__':
    mass_list = load_mass_list()
    print(mass_list)

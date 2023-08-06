from glycomass.mass_list import load_mass_list
from glycomass.process_data import process_folder
from glycomass.clustering import cluster
from pathlib import Path

mass_list = load_mass_list()
cols = list(mass_list.keys())

def run(folder_path, cols=cols, remove_prefix="", linkage='ward', distance_threshold=0.2, convert_well_names=True):
    df = process_folder(folder_path, mass_list, remove_prefix=remove_prefix, convert_well_names=convert_well_names)
    df = cluster(df, cols, distance_threshold=distance_threshold, linkage=linkage)
    Path(f"{folder_path}/result").mkdir(parents=True, exist_ok=True)
    df.to_excel(f"{folder_path}/result/processed_results.xlsx")

if __name__ == '__main__':
    folder_path = str(Path(__file__).parents[1]) + '/data/01Mar22'
    run(folder_path)


from sklearn.cluster import AgglomerativeClustering


def cluster(df, cols, distance_threshold=0.2, linkage='ward'):
    train_data = df[cols]
    agglo = AgglomerativeClustering(distance_threshold=distance_threshold, n_clusters=None, linkage=linkage)
    agglo.fit(train_data)
    df['labels'] = [str(l) for l in agglo.labels_]
    print(f"{len(df['labels'].unique())} clusters at distance {distance_threshold}")
    return df

if __name__ == '__main__':
    from pathlib import Path
    from glycomass.mass_list import load_mass_list
    from glycomass.process_data import process_data, process_folder

    mass_list = load_mass_list()
    folder_path = str(Path(__file__).parents[1]) + '/data/01Mar22'
    cols = list(mass_list.keys())  # ['1', '2', '3', '4', '5', '6', '7', '8']
    distance_threshold = 0.2
    linkage = 'ward'

    prefix = ""
    df = process_folder(folder_path, mass_list, remove_prefix=prefix)
    df = cluster(df, cols, distance_threshold=distance_threshold, linkage=linkage)

    Path(f"{folder_path}/result").mkdir(parents=True, exist_ok=True)
    df.to_excel(f"{folder_path}/result/processed_results.xlsx")

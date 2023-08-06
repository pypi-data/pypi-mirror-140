import pandas as pd
import numpy as np
from pathlib import Path
from glycomass.well_replacement import well_convert

def load_data(filepath):
    dict_of_dfs = pd.read_excel(filepath,
                                sheet_name=None,
                                skiprows=[0,1],
                                header=[0])
    return dict_of_dfs

def get_intensities(df, mass_list, mz_col='m/z', int_col='Intens.'):
    intensity_dict = {}
    for dp, mass_range in mass_list.items():
        df_range = df[(df[mz_col] >= mass_range[0]) & (df[mz_col] <= mass_range[1])]
        intensity = df_range[int_col].max()
        if intensity is np.nan:
            intensity = 0
        intensity_dict[dp] = intensity

    return intensity_dict

def get_intensity_ratios(intensity_dict, round_to=4):
    sum_intensity = sum(list(intensity_dict.values()))

    ratio_intensity_dict = {}
    for key, value in intensity_dict.items():
        ratio_intensity_dict[key] = round(value/sum_intensity, round_to)

    return ratio_intensity_dict

def process_data(filepath, mass_list, remove_prefix='', convert_well_names=True):
    dict_of_dfs = load_data(filepath)
    list_results_dicts = []
    for name, df in dict_of_dfs.items():
        intensity_dict = get_intensities(df, mass_list)
        ratio_intensity_dict = get_intensity_ratios(intensity_dict)
        name = name.replace(remove_prefix, '')
        if convert_well_names is True:
            name = well_convert(name)
        ratio_intensity_dict['name'] = name
        list_results_dicts.append(ratio_intensity_dict)

    final_df = pd.DataFrame(list_results_dicts)

    # reorder cols so name is first
    cols = cols = final_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    final_df = final_df[cols]
    return final_df

def process_folder(folder_path, mass_list, remove_prefix='', convert_well_names=True):

    pathlist = Path(folder_path).glob('*.xlsx')
    list_dfs = []
    for filepath in pathlist:
        df = process_data(filepath, mass_list, remove_prefix=remove_prefix, convert_well_names=convert_well_names)
        list_dfs.append(df)

    final_df = pd.concat(list_dfs)
    final_df = final_df.reindex()
    return final_df


if __name__ == '__main__':
    from glycomass.mass_list import load_mass_list

    mass_list = load_mass_list()
    filepath = str(Path(__file__).parents[0]) + '/data/test_data.xlsx'
    prefix = "Itag_assay_spot_"
    df = process_data(filepath, mass_list, remove_prefix=prefix)

    # save and print the test
    print(df.head())
    df.to_excel(str(Path(__file__).parents[0]) + '/data/test_results.xlsx')


    folder_path =  str(Path(__file__).parents[0]) + '/data/test_run'
    df = process_folder(folder_path, mass_list)
    print(df.head())
    Path(str(Path(__file__).parents[0]) + '/data/test_run/result').mkdir(parents=True, exist_ok=True)
    df.to_excel(str(Path(__file__).parents[0]) + '/data/test_run/result/test_results.xlsx')

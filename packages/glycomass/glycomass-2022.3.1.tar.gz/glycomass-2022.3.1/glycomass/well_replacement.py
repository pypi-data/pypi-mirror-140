import itertools

def get_well_replacement_dict():
    well_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    well_cols = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    wells_replace_cols = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    wells = [f"{w[0]}{w[1]}" for w in list(itertools.product(well_rows, well_cols))]
    wells_replace = [f"{w[0]}{w[1]}" for w in list(itertools.product(well_rows, wells_replace_cols))]
    return {w: r for w, r in zip(wells, wells_replace)}

well_replacement_dict = get_well_replacement_dict()

def well_convert(name, spacer='_'):
    '''Converts any wells in name to A01 format (from A1)'''
    for well, replacement in well_replacement_dict.items():
        well = f"{well}{spacer}"
        if well in name:
            replacement = f"{replacement}{spacer}"
            name = name.replace(well, replacement)
    return name

if __name__ == '__main__':
    test_name = 'this_is_a_test_A1'
    new_name = well_convert(test_name)
    print(new_name)
import pandas as pd
import PyCO2SYS as pyco2
import openpyxl
import numpy as np

"""Uses the PyPCO2Sys library to get calculated data. See the mix of params to calculate in order of priority in get_carbonate_params function
Also I specify some of the optional nutrients arguments if there is data available, if not will use PyPCO2Sys default values as seen in the else
statments of teh get_optional_nutrients function. I prepend co2Sys_ to all new variables that came from PyPCO2Sys, which includs input variables"""


def read_excel(file: str) -> pd.DataFrame:
    # Read the excel file and add the units to the headers

    # Read the file with both header and units rows
    df_header = pd.read_excel(file, nrows=2, dtype=str, header=None)

    # Get the column names (first row) and units (second row)
    headers = df_header.iloc[0].values
    units = df_header.iloc[1].values

    new_cols = []
    for header, unit in zip(headers, units):
        if pd.notna(unit) and unit != 'n.a.' and unit.strip() != '':
            new_cols.append(f"{header}.{unit}")
        else:
            new_cols.append(header)

    df = pd.read_excel(file, skiprows=2, names=new_cols)

    cleaned_df = clean_missing_data(df=df)
    final_df = cleaned_df.dropna(how='all')

    return final_df


def clean_missing_data(df: pd.DataFrame, missing_value=-999):
    """Replace missing data codes with NaN"""
    df_clean = df.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].replace(missing_value, np.nan)
    return df_clean


def get_carbonate_params(row):
    """Determine which two carbonate parameters to use"""
    if pd.notna(row['DIC.umol/kg']) and pd.notna(row['TA.umol/kg']):
        return row['DIC.umol/kg'], row['TA.umol/kg'], 2, 1  # DIC, TA
    elif pd.notna(row['DIC.umol/kg']) and pd.notna(row['pH_T_measured']):
        return row['DIC.umol/kg'], row['pH_T_measured'], 2, 3  # DIC, pH
    elif pd.notna(row['TA.umol/kg']) and pd.notna(row['pH_T_measured']):
        return row['TA.umol/kg'], row['pH_T_measured'], 1, 3
    else:
        return None, None, None, None


def get_optional_nutrients(row):

    # salinity
    if pd.notna(row['Salinity_PSS78']):
        salinity = row['Salinity_PSS78']
    elif pd.notna(row['CTDSAL_PSS78']):
        salinity = row['CTDSAL_PSS78']
    else:
        salinity = 35  # default in PyCO2SYS

    # Temperature
    if pd.notna(row['CTDTEMP_ITS90.deg_C']):
        temperature = row['CTDTEMP_ITS90.deg_C']
    else:
        temperature = 25  # default in PyCO2Sys

    # Pressure
    if pd.notna(row['CTDPRES.dbar']):
        pressure = row['CTDPRES.dbar']
    else:
        pressure = 0  # default in PyCo2Sys

    # silitcate
    if pd.notna(row['Silicate.umol/kg']):
        silicate = row['Silicate.umol/kg']
    else:
        silicate = 0  # default in PyCo2Sys

    # phosphate
    if pd.notna(row['Phosphate.umol/kg']):
        phosphate = row['Phosphate.umol/kg']
    else:
        phosphate = 0  # default in PyCo2Sys

    return salinity, temperature, pressure, silicate, phosphate


def get_pco2_info(row: pd.Series) -> int:
    # Get the saturation_aragonite using PyCO2SYS
    if pd.notna(row['par1']) or pd.notna(row['par2']):
        results = pyco2.sys(par1=row['par1'], par2=row['par2'], par1_type=row['par1_type'], par2_type=row['par2_type'], salinity=row['salinity'],
                            temperature=row['temperature'], pressure=row['pressure'], total_silicate=row['silicate'], total_phosphate=row['phosphate'])
        return pd.Series(results)
    else:
        return row


def main() -> None:

    df = read_excel('WCOA2021_Data_forSDIS_2022_09-28.xlsx')

    # Apply function to get parameters
    param_data = pd.DataFrame()
    param_data[['par1', 'par2', 'par1_type', 'par2_type']] = df.apply(
        get_carbonate_params, axis=1, result_type='expand')

    # Apply function to get optional arguments
    optional_nutrients = pd.DataFrame()
    optional_nutrients[['salinity', 'temperature', 'pressure', 'silicate', 'phosphate']] = df.apply(
        get_optional_nutrients, axis=1, result_type='expand')

    # conbine param and optional nutrient
    pyco2_df = pd.concat([param_data, optional_nutrients], axis=1)

    pco2_results_df = pyco2_df.apply(
        get_pco2_info, axis=1, result_type='expand')
    pco2_updated = pco2_results_df.add_prefix('co2Sys_')

    # Add saturated aragonite to df and save
    final_df_with_sat_arag = pd.concat([df, pco2_updated], axis=1)
    final_df_with_sat_arag.to_csv(
        'WCOA2021_Data_forSDIS_2022_09-23_with_pco2Sys_calcs.csv')


if __name__ == "__main__":
    main()

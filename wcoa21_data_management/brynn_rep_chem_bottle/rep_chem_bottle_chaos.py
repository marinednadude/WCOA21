import pandas as pd


def add_rep_chem_bottle_data():

    df = pd.read_csv('pre_rep_chem_merged_data_with_rep.csv')

    # Find all btl_ columns
    btl_cols = [c for c in df.columns if c.startswith('btl')]

    for btl_col in btl_cols:
        # Skip flag columns - they are handled when their parent columns are processed
        if btl_col.endswith('_flag'):
            continue

        rep_col = 'rep_' + btl_col
        if rep_col not in df.columns:
            continue

        # Find rows where btl_ value is NaN
        mask = df[btl_col].isna()
        if not mask.any():
            continue

        # Fill the main column
        df.loc[mask, btl_col] = df.loc[mask, rep_col]

        # Strip units suffix and build flag column name
        base = btl_col.rsplit('.')[0]
        print(base)
        flag_col = base + '_flag'
        rep_flag_col = 'rep_' + base + '_flag'
        if flag_col in df.columns and rep_flag_col in df.columns:
            df.loc[mask, flag_col] = df.loc[mask, rep_flag_col]

    return df


def add_nc_to_new_df(df):
    nc_df = pd.read_csv(
        '/Users/zalmanek/Development/WCOA21/wcoa21_data_management/FinalOME_Merge_nc_samp_added.csv')

    nc_row = nc_df[nc_df['Sample_Name'].str.contains(
        '.NC', regex=False)].iloc[0:1]

    final_df = pd.concat([df, nc_row], ignore_index=True)

    return final_df


df = add_rep_chem_bottle_data()
final_df = add_nc_to_new_df(df=df)

final_df.to_csv('FinalOME_Merge_with_rep_chem_bottles.csv', index=False)

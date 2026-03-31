# The initial R script - MergeScript_WCOA21_20250520.rmd did not use files that included
# the E610.NC samples so this sample was missing. Need to add it back in.

import pandas as pd
import gspread #library that makes it easy for us to interact with the sheet
from google.oauth2.service_account import Credentials

def load_google_sheet_as_df(google_sheet_id: str, sheet_name: str, header: int, google_sheet_json_cred: str) -> pd.DataFrame:
        """
        Load a google sheet as a data frame. The google_sheet_json_cred is the path to the credentials.json file 
        with credentials for acessing google sheets programatically."""

        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        creds = Credentials.from_service_account_file(google_sheet_json_cred, scopes=scopes)
        client = gspread.authorize(creds)

        sheet = client.open_by_key(google_sheet_id)
        worksheet = sheet.worksheet(sheet_name)
        
        # Get all values
        values = worksheet.get_all_values()
        headers = values[header]
        data_rows = values[header+1:]
        df = pd.DataFrame(data_rows, columns=headers)
        
        return df


def main():
    
    sample_needed = 'E610.NC.WCOA21' # (.WCOA21 will get added later along with the other samples)
    ome_sample_sheet_df = load_google_sheet_as_df(google_sheet_id='1Fw1Bk81wrZsztWo-Ef_qnuUdHhnVk0Q7IVmkvQaQ9-I',
                                                  sheet_name='Environmental Samples',
                                                  header=0,
                                                  google_sheet_json_cred='/home/poseidon/zalmanek/FAIRe-Mapping/credentials.json')
    

    samp_df = ome_sample_sheet_df[ome_sample_sheet_df['FINAL Sample NAME'] == sample_needed]

    final_merge_df = pd.read_csv('/home/poseidon/zalmanek/WCOA21/wcoa21_data_management/FinalOME_Merge_WCOA21_sample_data.csv')
    new_data = {
         'Sample_Name': samp_df.iloc[0]['FINAL Sample NAME'].replace('.WCOA21', ''),
         'Negative_control': 'TRUE',
         'Cruise_ID_short': 'WCOA21',
         'Cruise_ID_long': '2021_WCOA_RonBrown',
         'Collection_Date_UTC': samp_df.iloc[0]['Collection Date (UTC)']
         }
    new_row_df = pd.DataFrame([new_data])
    final_df = pd.concat([final_merge_df, new_row_df], ignore_index=True)
    final_df.fillna('')

    final_df.to_csv('/home/poseidon/zalmanek/WCOA21/wcoa21_data_management/FinalOME_Merge_nc_samp_added.csv')
    

if __name__ == "__main__":
    main()
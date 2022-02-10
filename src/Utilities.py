'''
StratzToGo Utility Functions
'''

import os
import pandas as pd

def clean_csv_file(file_name):
    if os.path.isfile(file_name + '.csv'):
        file_df = pd.read_csv(file_name + '.csv')
        file_df.drop_duplicates(keep="first", inplace=True)
        file_df.to_csv(file_name + '.csv', index=False)
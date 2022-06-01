from pandas.core.frame import DataFrame
import requests
import pandas
import csv
import json
from bs4 import BeautifulSoup
import math

def make_lane_stats_df(lane):
    # Request the dotabuff lanes page for given lane and soupify
    r = requests.get('https://www.dotabuff.com/heroes/lanes?lane=' + lane,
                     headers={'user-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content)

    # Process table from html to JSON to dataframe
    table = soup('table')[0]
    headers = [th.text for th in table ('th')]
    rows = [x[1:] for x in
            [[td.text for td in tr('td')] for tr in table.tbody('tr')]]
    stats = [dict(zip(headers, row)) for row in rows]
    
    # Making dictionary then exporting it to json
    stats_df = pandas.concat((pandas.json_normalize(d) for d in stats), axis=0)
    hero_ids = pandas.read_csv("Hero_Ids.csv")

    # Cross reference stats dataframe and hero ids
    # Add a placeholder if hero isn't in the dataframe
    for index, row in hero_ids.iterrows():
        if not stats_df['Hero'].str.contains(row['hero_name']).any():
            stats_df = stats_df.append({'Hero':row['hero_name']},
                                       ignore_index=True)

    return(stats_df)

def get_dotabuff_hero_lane_data():
    # Adding an extra column for lanes to match up with positions 
    lanes = ['safe', 'mid', 'off', 'off', 'safe', 'jungle', 'roaming']
    positions = [1, 2, 3, 4, 5, 6, 7]

    # Gather all the lane stats into a single dataframe
    all_lane_stats_df = pandas.DataFrame()
    for lane, position in zip(lanes, positions):
        lane_stats_df = make_lane_stats_df(lane)
        lane_stats_df['Roles'] = position
        all_lane_stats_df = pandas.concat([all_lane_stats_df, lane_stats_df])
    
    # Reset index values since combining the dataframes resulted in multiple
    # rows for each index value (i.e. 7 different rows with index 1)
    all_lane_stats_df = all_lane_stats_df.reset_index()
    del all_lane_stats_df['index']
    
    # Convert data columns to floats
    all_lane_stats_df['Presence'] = \
        all_lane_stats_df['Presence'].str.rstrip('%').astype('float') / 100.0
    all_lane_stats_df['Win Rate'] = \
        all_lane_stats_df['Win Rate'].str.rstrip('%').astype('float') / 100.0
    all_lane_stats_df['KDA Ratio'] = \
        all_lane_stats_df['KDA Ratio'].astype('float')
    all_lane_stats_df['GPM'] = all_lane_stats_df['GPM'].astype('float')
    all_lane_stats_df['XPM'] = all_lane_stats_df['XPM'].astype('float')

    # Replace placeholder stats with the average of other lanes
    final_lane_stats_df = all_lane_stats_df
    for index, row in final_lane_stats_df.iterrows():
        if math.isnan(row['Presence']):
            final_lane_stats_df.at[index, 'Presence'] = 0
            final_lane_stats_df.at[index, 'Win Rate'] = \
                all_lane_stats_df[all_lane_stats_df.Hero ==
                                  row['Hero']]['Win Rate'].mean()
            final_lane_stats_df.at[index, 'KDA Ratio'] = \
                all_lane_stats_df[all_lane_stats_df.Hero ==
                                  row['Hero']]['KDA Ratio'].mean()
            final_lane_stats_df.at[index, 'GPM'] = \
                all_lane_stats_df[all_lane_stats_df.Hero ==
                                  row['Hero']]['GPM'].mean()
            final_lane_stats_df.at[index, 'XPM'] = \
                all_lane_stats_df[all_lane_stats_df.Hero ==
                                  row['Hero']]['XPM'].mean()

    # Save the results to csv for future reference
    final_lane_stats_df.to_csv('statsbylane.csv', index=False, encoding='utf-8')


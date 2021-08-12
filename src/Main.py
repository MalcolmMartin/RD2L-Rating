'''
StratzToGo
'''

import sys
import os
import requests
import json
import pandas as pd
import numpy as np
from Laning import add_roles, calculate_laning_advantage
from Game import calculate_game_advantages

# TODO: Scale how good their hero is in the game or get a draft advantage number

# Lets special characters be printed to console (comment out when done)
sys.stdout.reconfigure(encoding='utf-8')

# Hero id to hero name translator
hero_id_df = pd.read_csv('Hero_Ids.csv')

# Displays entire table instead of sample
pd.set_option("display.max_rows", None, "display.max_columns", None)

def add_dotabuff_data(match_data_df):
    # TODO: have not is_radiant condition and swap 1/3
    hero_lane_stats_df = pd.read_csv('statsbylane.csv')
    # Hero lane stats
    conditions = [
        (hero_lane_stats_df['Roles'] == 'off'),
        (hero_lane_stats_df['Roles'] == 'mid'),
        (hero_lane_stats_df['Roles'] == 'safe'),
        (hero_lane_stats_df['Roles'] == 'jungle'),
        (hero_lane_stats_df['Roles'] == 'roaming')]
    values = ['3', '2', '1', '4', '4']
    hero_lane_stats_df['lane'] = np.select(conditions, values)
    hero_lane_stats_df['hero_lane'] = hero_lane_stats_df['Hero'] + '_' + hero_lane_stats_df['lane']
    hero_lane_stats_dict = hero_lane_stats_df.set_index('hero_lane').T.to_dict('list')
    # Dictionary Indices: 0 - Hero, 1 - Presence, 2 - Win Rate, 3 - KDA Ratio,
    # 4 - GPM, 5 - XPM, 6 - Roles, 7 - lane, 8 - hero_lane
    
    # Get expected hero lane kda from dotabuff data
    # Swap lanes for dire so it matches safe/off instead of top/bot
    for index, row in match_data_df.iterrows():
        if (row['lane'] == '1') & (row['isRadiant'] == False):
            match_data_df.at[index,'lane'] = 3
        elif (row['lane'] == '3') & (row['isRadiant'] == False):
            match_data_df.at[index,'lane'] = 1
    
    # Put in hero_lane data from dotabuff
    match_data_df['lane'] = match_data_df['lane'].map(str)
    match_data_df['kda_lookup_value'] = match_data_df['hero_name'] + '_' + match_data_df['lane']
    for index, row in match_data_df.iterrows():
        match_data_df.at[index,'hero_lane_kda'] = hero_lane_stats_dict[row['kda_lookup_value']][3]
        match_data_df.at[index,'hero_lane_gpm'] = hero_lane_stats_dict[row['kda_lookup_value']][4]
        match_data_df.at[index,'hero_lane_xpm'] = hero_lane_stats_dict[row['kda_lookup_value']][5]
    
    return match_data_df

def add_lane_timings(laning_df, category):
    # Pull the value for 5 and 10 minutes to more easily manipulate
    laning_df[category + "_5"] = [x[5] for x in laning_df[category + "_t"]]
    laning_df[category + "_10"] = [x[10] for x in laning_df[category + "_t"]]
    
    return laning_df

def process_player_match_df(opendota_player_match_df):
    # Create a laning dataframe from match df
    laning_df = opendota_player_match_df[[
        "personaname", "hero_id", "hero_name", "rank_tier", "isRadiant",
        "lane", "gold_t", "xp_t", "lh_t", "dn_t", "benchmarks.lhten.raw",
        "benchmarks.lhten.pct", "lane_efficiency_pct"]]
    laning_df['role'] = ""
    laning_df['lane_advantage'] = 0
    
    # Add columns for 5 and 10 minutes
    for category in ['gold', 'xp', 'lh', 'dn']:
        laning_df = add_lane_timings(laning_df, category)
    
    # Split laning data into team-lane combinations and put in dictionary
    lanes_dict = {}
    lanes_dict['radiant_bot'] = laning_df[(laning_df['lane']==1) &
                                         (laning_df['isRadiant']==True)]
    lanes_dict['dire_bot'] = laning_df[(laning_df['lane']==1) &
                                      (laning_df['isRadiant']==False)]
    lanes_dict['radiant_mid'] = laning_df[(laning_df['lane']==2) &
                                         (laning_df['isRadiant']==True)]
    lanes_dict['dire_mid'] = laning_df[(laning_df['lane']==2) &
                                      (laning_df['isRadiant']==False)]
    lanes_dict['radiant_top'] = laning_df[(laning_df['lane']==3) &
                                         (laning_df['isRadiant']==True)]
    lanes_dict['dire_top'] = laning_df[(laning_df['lane']==3) &
                                      (laning_df['isRadiant']==False)]
    
    # Add roles
    lanes_dict = add_roles(lanes_dict)
    
    # Calculate laning Advantage
    laning_data = calculate_laning_advantage(lanes_dict)
    
    # Pull only the columns for determining non-laning game performance
    processed_match_data = \
        opendota_player_match_df[
            ["personaname", "hero_id", "hero_name", "rank_tier",
             "isRadiant", "lane", "win", "hero_damage", "tower_damage",
             "hero_healing", "stuns", "kills", "deaths", "assists",
             "last_hits", "lh_t", "denies", "benchmarks.gold_per_min.raw",
             "benchmarks.xp_per_min.raw",
             "benchmarks.last_hits_per_min.pct",
             "benchmarks.hero_damage_per_min.pct",
             "benchmarks.hero_healing_per_min.pct",
             "benchmarks.tower_damage.pct",
             "benchmarks.stuns_per_min.pct"]]
    
    # Combine game data and laning data
    processed_match_data = processed_match_data.combine_first(laning_data)
    for advantage in ['combat', 'hd', 'farm', 'td', 'utility', 'total']:
        processed_match_data[advantage + '_advantage'] = 0
    
    # Get hero lane dotabuff data
    processed_match_data = add_dotabuff_data(processed_match_data)
    
    # Calculate game advantages
    processed_match_data = calculate_game_advantages(processed_match_data)
    
    # Combine all advantages into a single value
    for adv_type in ['lane', 'combat', 'hd', 'farm', 'td', 'utility']:
        processed_match_data['total_advantage'] += \
            processed_match_data[adv_type + '_advantage']
    
    return processed_match_data

def request_opendota_player_match_df(match_id):
    # Grab match data
    opendota_request = \
        requests.get("https://api.opendota.com/api/matches/" + match_id)
    
    # Translates the JSON response to a pandas dataframe
    # Only grabs and flattens the player data
    opendota_match_json_data = json.loads(opendota_request.text)
    opendota_player_match_df = \
        pd.json_normalize(opendota_match_json_data, record_path=["players"])
    
    # Save match data to csv so api only gets called once per match
    opendota_player_match_df.to_csv(
        'Opendota_Requests\\' + match_id + '.csv',
        encoding='utf-8', index=False)
    
    return opendota_player_match_df

def get_opendota_player_match_df(match_id):
    # Read match data from csv, request from opendota otherwise
    if os.path.isfile('Opendota_Requests\\' + match_id + '.csv'):
        opendota_player_match_df = \
            pd.read_csv('Opendota_Requests\\' + match_id + '.csv')
        # Use json.loads on these series to parse the loaded json strings
        for category in ['gold', 'xp', 'lh', 'dn']:
            opendota_player_match_df[category + "_t"] = \
            [json.loads(x) for x in opendota_player_match_df[category + "_t"]]
    else:
        opendota_player_match_df = request_opendota_player_match_df(match_id)
    
    return opendota_player_match_df

def process_match_id(match_id):
    # Retrieve opendota data from api request or disk
    opendota_player_match_df = get_opendota_player_match_df(match_id)
    
    # Join with hero_id_df to get hero name
    opendota_player_match_df = \
        opendota_player_match_df.join(
            hero_id_df.set_index('hero_id'), on='hero_id')
    
    # Run the evaluation algorithm
    processed_match_df = process_player_match_df(opendota_player_match_df)
    
    # Save processed match data
    processed_match_df.to_csv('Processed\\' + match_id +
                              '_processed.csv', encoding='utf-8', index=False)
    
    #print(processed_match_df)
    
    print(processed_match_df['hero_name'])
    
    for advantage in ['lane', 'combat', 'hd', 'farm', 'td', 'utility', 'total']:
        print(processed_match_df[advantage + '_advantage'])

def main():
    # RD2L test game
    process_match_id("6084550449")
    
    #process_match_id("6126964330")

main()
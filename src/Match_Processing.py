'''
StratzToGo Match Processing
'''
import json
import math
import os
import pandas as pd
import requests
from Laning import add_roles, calculate_laning_advantage
from Game import calculate_game_advantages

def add_dotabuff_data(match_data_df):
    # Read dotabuff data into a df and make a new column that is hero_role
    # (1-5, 6-jungle, 7-roaming)
    hero_lane_stats_df = pd.read_csv('statsbylane.csv')
    hero_lane_stats_df['Roles'] = hero_lane_stats_df['Roles'].astype(str)
    hero_lane_stats_df['hero_role'] = \
        hero_lane_stats_df['Hero'] + '_' + hero_lane_stats_df['Roles']
    hero_lane_stats_dict = \
        hero_lane_stats_df.set_index('hero_role').T.to_dict('list')
    # Dictionary Indices: 0 - Hero, 1 - Presence, 2 - Win Rate, 3 - KDA Ratio,
    # 4 - GPM, 5 - XPM, 6 - Roles
    
    # Get expected hero role stats from dotabuff data
    match_data_df['dotabuff_lookup_value'] = match_data_df['hero_name'] + \
        '_' + match_data_df['role']
    for index, row in match_data_df.iterrows():
        match_data_df.at[index,'hero_lane_kda'] = \
            hero_lane_stats_dict[row['dotabuff_lookup_value']][3]
        match_data_df.at[index,'hero_lane_gpm'] = \
            hero_lane_stats_dict[row['dotabuff_lookup_value']][4]
        match_data_df.at[index,'hero_lane_xpm'] = \
            hero_lane_stats_dict[row['dotabuff_lookup_value']][5]
    
    return match_data_df

def add_lane_timings(laning_df, category):
    # Pull the value for 5 and 10 minutes to more easily manipulate
    laning_df[category + "_5"] = [x[5] for x in laning_df[category + "_t"]]
    laning_df[category + "_10"] = [x[10] for x in laning_df[category + "_t"]]
    
    return laning_df

def process_player_match_df(match_id, opendota_player_match_df):
    # Create a laning dataframe from match df
    laning_df = opendota_player_match_df[[
        "personaname", "hero_id", "hero_name", "rank_tier", "isRadiant",
        "lane", "gold_t", "xp_t", "lh_t", "dn_t", "lane_efficiency_pct"]]
    laning_df['role'] = ''
    laning_df['lane_advantage'] = 0
    
    # Add columns for 5 and 10 minutes
    for category in ['gold', 'xp', 'lh', 'dn']:
        laning_df = add_lane_timings(laning_df, category)
    
    # Add columns for support and core averages
    for category in ['gold', 'xp', 'lh', 'dn']:
        laning_df['core_' + category + '_5'] = 0
        laning_df['core_' + category + '_10'] = 0
        laning_df['support_' + category + '_5'] = 0
        laning_df['support_' + category + '_10'] = 0
    
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
    lanes_dict['radiant_jungle'] = laning_df[((laning_df['lane']==4) |
                                              (laning_df['lane']==5)) &
                                             (laning_df['isRadiant']==True)]
    lanes_dict['dire_jungle'] = laning_df[((laning_df['lane']==4) |
                                           (laning_df['lane']==5)) &
                                             (laning_df['isRadiant']==False)]
    
    # Add roles
    lanes_dict = add_roles(lanes_dict)
    
    # Calculate laning Advantage
    laning_data = calculate_laning_advantage(lanes_dict)
    
    # Pull only the columns for determining non-laning game performance
    processed_match_data = \
        opendota_player_match_df[
            ["leagueid", "match_id", "account_id", "personaname", "hero_id",
             "hero_name", "rank_tier", "isRadiant", "lane", "win",
             "hero_damage", "tower_damage", "hero_healing", "stuns", "kills",
             "deaths", "assists", "last_hits", "lh_t", "denies",
             "benchmarks.gold_per_min.raw", "benchmarks.xp_per_min.raw",
             "benchmarks.last_hits_per_min.pct",
             "benchmarks.hero_damage_per_min.pct",
             "benchmarks.hero_healing_per_min.pct",
             "benchmarks.tower_damage.pct"]]
    
    # Combine game data and laning data
    processed_match_data = processed_match_data.combine_first(laning_data)
    for advantage in ['combat', 'hd', 'farm', 'td', 'utility', 'total']:
        processed_match_data[advantage + '_advantage'] = float(0)
    
    # Get hero lane dotabuff data
    processed_match_data = add_dotabuff_data(processed_match_data)
    
    # Calculate game advantages
    processed_match_data = calculate_game_advantages(processed_match_data)
    
    # Combine all advantages into a single value
    for adv_type in ['lane', 'combat', 'hd', 'farm', 'td', 'utility']:
        processed_match_data['total_advantage'] += \
            processed_match_data[adv_type + '_advantage']
    
    return processed_match_data

def process_match_id(match_id, opendota_player_match_df):
    # Hero id to hero name translator
    hero_id_df = pd.read_csv('Hero_Ids.csv')
    
    # Join with hero_id_df to get hero name
    opendota_player_match_df = \
        opendota_player_match_df.join(
            hero_id_df.set_index('hero_id'), on='hero_id')
    
    # Run the evaluation algorithm
    processed_match_df = process_player_match_df(match_id, opendota_player_match_df)
    
    # Save processed match data
    processed_match_df.to_csv('Processed\\' + match_id +
                              '_processed.csv', encoding='utf-8', index=False)
    
    return processed_match_df

def request_opendota_player_match_df(match_id):
    # Read match data from file or request from opendota otherwise
    # TODO: Debug why reading from file causes an error
    if os.path.isfile('Opendota_Requests\\' + match_id + '.csv'):
        opendota_match_df = \
            pd.read_csv('Opendota_Requests\\' + match_id + '.csv')
        if math.isnan(opendota_match_df['version'].iloc[0]):
            return pd.DataFrame()
        # Use json.loads on these series to parse as objects instead of strings
        for category in ['gold', 'xp', 'lh', 'dn']:
            opendota_match_df[category + "_t"] = \
                [json.loads(x) for x in opendota_match_df[category + "_t"]]
    else:
        # Request match data
        opendota_request = \
            requests.get("https://api.opendota.com/api/matches/" + match_id)
        
        # Translate the JSON response to a pandas dataframe
        opendota_match_json_data = json.loads(opendota_request.text)
        
        # Use the players section as the data and the meta data as league id
        # Can add more meta data as required
        opendota_match_df = pd.json_normalize(
            opendota_match_json_data, 'players', meta=['leagueid', 'version'])
        
        # Add column for match_id
        opendota_match_df['match_id'] = match_id
        
        # Save to file
        opendota_match_df.to_csv('Opendota_Requests\\' + match_id + '.csv',
                       encoding='utf-8', index=False)
    
        if opendota_match_df['version'].iloc[0] == None:
            return pd.DataFrame()
    
    return opendota_match_df

def get_processed_match_df(match_id):
    # Read processed match data from csv if available,
    # request from opendota otherwise and process
    if os.path.isfile('Processed\\' + match_id + '_processed.csv'):
        opendota_processed_player_match_df = \
            pd.read_csv('Processed\\' + match_id + '_processed.csv')
        # Return empty dataframe if replay is not parsed
        if opendota_processed_player_match_df.empty:
            print ('Replay not parsed')
            return pd.DataFrame()
        # Use json.loads on these series to parse as objects instead of strings
        for category in ['gold', 'xp', 'lh', 'dn']:
            opendota_processed_player_match_df[category + "_t"] = \
                [json.loads(x) for x in
                 opendota_processed_player_match_df[category + "_t"]]
    else:
        opendota_player_match_df = request_opendota_player_match_df(match_id)
        # Return empty dataframe if replay is not parsed
        if opendota_player_match_df.empty:
            print ('Replay not parsed')
            return pd.DataFrame()
        opendota_processed_player_match_df = \
            process_match_id(match_id, opendota_player_match_df)
    
    return opendota_processed_player_match_df
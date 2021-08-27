'''
StratzToGo
'''

import sys
import os
import requests
import json
import fileinput
import math
import pandas as pd
from Match_Processing import process_match_id
from OriginalLoop import get_dotabuff_hero_lane_data

# TODO: Scale how good their hero is in the game or get a draft advantage number

# Lets special characters be printed to console (comment out when done)
sys.stdout.reconfigure(encoding='utf-8')

# Displays entire table instead of sample, max decimals 3
pd.set_option("display.max_rows", None, "display.max_columns",
              None, "display.precision", 3)

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
        
        # Save to file
        opendota_match_df.to_csv('Opendota_Requests\\' + match_id + '.csv',
                       encoding='utf-8', index=False)
    
        if opendota_match_df['version'].iloc[0] == None:
            return pd.DataFrame()
    
    return opendota_match_df

def get_processed_player_match_df(match_id):
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
                [json.loads(x) for x in opendota_processed_player_match_df[category + "_t"]]
    else:
        opendota_player_match_df = request_opendota_player_match_df(match_id)
        # Return empty dataframe if replay is not parsed
        if opendota_player_match_df.empty:
            print ('Replay not parsed')
            return pd.DataFrame()
        opendota_processed_player_match_df = process_match_id(match_id, opendota_player_match_df)
    
    return opendota_processed_player_match_df

def get_league_match_ids(player_id):
    # Grab last 40 practice matches for player_id
    opendota_request = \
        requests.get("https://api.opendota.com/api/players/" +
                     player_id + "/matches/?lobby_type=1&limit=40")
    
    # Load the data into a dataframe
    opendota_match_json_data = json.loads(opendota_request.text)
    opendota_player_league_matches_df = \
        pd.json_normalize(opendota_match_json_data)
    
    # Filter left games/bad lobbys
    opendota_player_league_matches_df = opendota_player_league_matches_df[opendota_player_league_matches_df['leaver_status']==0]
    
    # Only return the match_id column
    return opendota_player_league_matches_df['match_id']

def get_player_match_stats(player_id):
    # Get all necessary league games, convert to strings
    match_ids = get_league_match_ids(player_id)
    match_ids = [str(x) for x in match_ids]
    
    # Get processed match data for all match_ids
    player_match_data_list = []
    for match_id in match_ids:
        player_match_data_list.append(get_processed_player_match_df(match_id))
    
    # Concatenate into a single dataframe
    player_match_data_df = pd.concat(player_match_data_list, ignore_index=True)
    
    # Filter for only desired player
    player_match_data_df = player_match_data_df[player_match_data_df['account_id']==int(player_id)]
    
    # Get only desired columns
    player_match_data_df = player_match_data_df[[
        "leagueid", "account_id", "personaname", "rank_tier", "hero_name",
        "role", "total_advantage", "lane_advantage", "combat_advantage",
        "hd_advantage", "farm_advantage", "td_advantage", "utility_advantage"]]
    
    # Save to csv for potential retrieval
    player_match_data_df.to_csv('Player Summary\\' + player_id + '.csv',
                                encoding='utf-8', index=False)
    
    return player_match_data_df

def quick_rd2l_stats(player_summary_df):
    player_summary_df['leagueid'] = player_summary_df['leagueid'].astype(str)
    player_summary_df = player_summary_df[player_summary_df['leagueid']=="13185"]
    player_summary_df['role_count'] = 0
    for index, row in player_summary_df.iterrows():
        player_summary_df.at[index, 'role_count'] = (player_summary_df.role.values == row['role']).sum()
    player_summary_df = player_summary_df.groupby('role').mean()
    return player_summary_df

def read_player_summary(player_id):#, league_id):
    player_summary_df = \
        pd.read_csv('Player Summary\\' + player_id + '.csv')
    
    #player_summary_df = player_summary_df.groupby('leagueid').mean()
    
    return player_summary_df

def main():
    # TODO: Add options for league filtering, columns to print, etc.
    # Accept instructions in "type id" format
    for line in fileinput.input():
        instructions = line.split()
        if instructions[0] == "dotabuff":
            get_dotabuff_hero_lane_data()
            print("Dotabuff successfully scraped")
        elif instructions[0] == "player":
            result_df = get_player_match_stats(instructions[1])
            result_df = read_player_summary(instructions[1])
            result_df = quick_rd2l_stats(result_df)
            result_df.to_csv('rd2l_season23.csv', mode='a', header=False)
            print("done")
        elif instructions[0] == "league":
            result_df = read_player_summary(instructions[1])#, instructions[2])
            result_df = quick_rd2l_stats(result_df)
            result_df.to_csv('rd2l_season23.csv', mode='a', header=False)
            print("done")
        elif instructions[0] == "match":
            result_df = get_processed_player_match_df(instructions[1])
        elif instructions[0] == "test":
            get_processed_player_match_df(instructions[1])
            print("done")

main()
'''
StratzToGo
'''

import sys
import os
import requests
import json
import pandas as pd
from Match_Processing import process_match_id

# TODO: Scale how good their hero is in the game or get a draft advantage number

# Lets special characters be printed to console (comment out when done)
sys.stdout.reconfigure(encoding='utf-8')

# Displays entire table instead of sample
pd.set_option("display.max_rows", None, "display.max_columns", None)

def request_opendota_player_match_df(match_id):
    # Grab match data
    opendota_request = \
        requests.get("https://api.opendota.com/api/matches/" + match_id)
    
    # Translates the JSON response to a pandas dataframe
    opendota_match_json_data = json.loads(opendota_request.text)
    
    # Add filter to league_id here and handle not repeating this call somehow (empty processed file?)
    test_df = pd.json_normalize(opendota_match_json_data)
    print(test_df)
    
    # Only grabs and flattens the player data
    opendota_player_match_df = \
        pd.json_normalize(opendota_match_json_data, record_path=["players"])
    
    # TODO: Make custom order of columns
    # Save match data to csv so match processing is only done once
    opendota_player_match_df.to_csv(
        'Opendota_Requests\\' + match_id + '.csv',
        encoding='utf-8', index=False)
    
    return opendota_player_match_df

def get_processed_player_match_df(match_id):
    # Read processed match data from csv if available, request from opendota otherwise and process
    if os.path.isfile('Processed\\' + match_id + '_processed.csv'):
        opendota_processed_player_match_df = \
            pd.read_csv('Processed\\' + match_id + '_processed.csv')
        # Use json.loads on these series to parse as objects instead of strings
        for category in ['gold', 'xp', 'lh', 'dn']:
            opendota_processed_player_match_df[category + "_t"] = \
            [json.loads(x) for x in opendota_processed_player_match_df[category + "_t"]]
    else:
        opendota_player_match_df = request_opendota_player_match_df(match_id)
        opendota_processed_player_match_df = process_match_id(match_id, opendota_player_match_df)
    
    return opendota_processed_player_match_df

def get_league_match_ids(player_id):
    # Grab last 100? practice matches for player_id
    # Temporarily 2
    opendota_request = \
        requests.get("https://api.opendota.com/api/players/" +
                     player_id + "/matches/?lobby_type=1&limit=2&leaver_status=0")
    
    # Load the data into a dataframe
    opendota_match_json_data = json.loads(opendota_request.text)
    opendota_player_league_matches_df = \
        pd.json_normalize(opendota_match_json_data)
    
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
    
    return player_match_data_df

def main():
    # RD2L test game
    #process_match_id("6084550449")
    
    x = get_processed_player_match_df("6146125511")
    print(x['hero_name'])
    
    for advantage in ['lane', 'combat', 'hd', 'farm', 'td', 'utility', 'total']:
        print(x[advantage + '_advantage'])
    
    
    #processed_player_df = get_player_match_stats("96324191")
    
    #print(processed_player_df['hero_name'])
    
    #for advantage in ['lane', 'combat', 'hd', 'farm', 'td', 'utility', 'total']:
    #    print(processed_player_df[advantage + '_advantage'])

main()
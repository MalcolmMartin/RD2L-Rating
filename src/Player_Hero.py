import requests
import json
import pandas as pd

def get_best_heroes(player_id):
    # Hero id to hero name translator
    hero_id_df = pd.read_csv('Hero_Ids.csv')
    
    # Grab heroes for player_id
    opendota_request = \
        requests.get("https://api.opendota.com/api/players/" +
                     player_id + "/heroes")
    
    # Load the data into a dataframe
    player_hero_json_data = json.loads(opendota_request.text)
    player_hero_df = \
        pd.json_normalize(player_hero_json_data)
    
    player_hero_games = player_hero_df['games'].sum()
    player_hero_df['play_percentage'] = player_hero_df['with_games'] / player_hero_games
    player_hero_df['type'] = 'All-Time'
    
    # Grab heroes for player_id in last year
    opendota_request = \
        requests.get("https://api.opendota.com/api/players/" +
                     player_id + "/heroes/?date=365")
    
    # Load the data into a dataframe
    player_hero_last_year_json_data = json.loads(opendota_request.text)
    player_hero_last_year_df = \
        pd.json_normalize(player_hero_last_year_json_data)
    
    player_hero_last_year_games = player_hero_last_year_df['games'].sum()
    player_hero_last_year_df['play_percentage'] = player_hero_last_year_df['with_games'] / player_hero_last_year_games
    player_hero_last_year_df['type'] = 'last Year'
    
    # Join with hero_id_df to get hero name
    #player_hero_last_year_df = \
    #    player_hero_last_year_df.join(
    #        hero_id_df.set_index('hero_id'), on='hero_id')
    
    player_hero_df = pd.concat([player_hero_df, player_hero_last_year_df])
    player_hero_df['hero_id'] = player_hero_df['hero_id'].astype(int)
    
    # Join with hero_id_df to get hero name
    player_hero_df = \
        player_hero_df.join(
            hero_id_df.set_index('hero_id'), on='hero_id')
    
    #df.sort_values(by=['col1'])
    
    return player_hero_df

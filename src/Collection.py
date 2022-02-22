'''
StratzToGo Collection Functions
'''

import numpy as np
import os
import pandas as pd

def add_to_collection(collection_name, match_df):
    # Save entire dataframe
    file_exists = os.path.isfile('Collections\\' + collection_name + '.csv')
    match_df.to_csv('Collections\\' + collection_name + '.csv', mode='a',
                    header=not file_exists, index=False)
    
    # Get only desired columns for summary, then save
    match_df = match_df[[
        "leagueid", "match_id", "account_id", "personaname", "rank_tier",
        "hero_name", "role", "total_advantage", "lane_advantage",
        "combat_advantage", "hd_advantage", "farm_advantage", "td_advantage",
        "utility_advantage"]]
    file_exists = os.path.isfile('Collections\\' + collection_name +
                                 '_short.csv')
    match_df.to_csv('Collections\\' + collection_name + '_short.csv',
                    mode='a', header=not file_exists, index=False)
    
    return

def collection_summary(collection_name):
    if os.path.isfile('Collections\\' + collection_name + '.csv'):
        collection_df = pd.read_csv('Collections\\' + collection_name + '.csv')
        collection_df['role_count'] = collection_df.groupby(
            ['account_id', 'role'])['total_advantage'].transform('count')
        collection_df = collection_df[[
            "account_id", 'role', 'role_count', "total_advantage",
            "lane_advantage", "combat_advantage", "hd_advantage",
            "farm_advantage", "td_advantage", "utility_advantage"]]
        collection_grouped_df = collection_df.groupby(
            ['account_id', 'role', 'role_count'])[[
                'total_advantage', 'lane_advantage', "combat_advantage",
                "hd_advantage", "farm_advantage", "td_advantage",
                "utility_advantage"]].mean()
        collection_grouped_df = collection_grouped_df.reset_index()
        collection_grouped_df.to_csv(
            'Collections\\' + collection_name + '_summary.csv', index=False)
    else:
        print("Collection does not exist")
    
    return

def identify_in_summary(collection_name, player_filename):
    if not os.path.isfile('Collections\\' + collection_name + '_summary.csv'):
        print("Collection does not exist")
    elif not os.path.isfile('Collections Lookups\\' + player_filename + '.csv'):
        print("Player file does not exist")
    else:
        collection_df = pd.read_csv('Collections\\' + collection_name +
                                    '_summary.csv')
        player_identification_df = pd.read_csv('Collections Lookups\\' +
                                               player_filename + '.csv')
        # Join with player identification
        collection_df = collection_df.join(
            player_identification_df.set_index('account_id'), on='account_id')
        collection_df.to_csv(
            'Collections\\' + collection_name + '_summary_identified.csv',
            index=False)
    
    return

def split_by_role_and_save(collection_name, identified_collection_df, role):
    role_rankings_df = identified_collection_df[
        identified_collection_df['role']==role]
    role_rankings_df = role_rankings_df.sort_values(
        by=['total_advantage'], ascending=False)
    role_rankings_df.to_csv('Collections Rankings\\position_' + str(role) +
                            '_' + collection_name + '_rankings.csv',
                            index=False)

def rank_identified_collection(collection_name):
    if not os.path.isfile('Collections\\' + collection_name +
                          '_summary_identified.csv'):
        print("Identified collection does not exist")
    else:
        identified_collection_df = pd.read_csv('Collections\\' +
                                               collection_name +
                                               '_summary_identified.csv')
        identified_collection_df['player'] = \
            identified_collection_df['player'].astype(str)
        identified_collection_df = identified_collection_df[
            identified_collection_df['player']!="nan"]
        role_count_maxes = identified_collection_df.groupby(
            ['team', 'role']).role_count.transform(max)
        identified_collection_df = identified_collection_df.loc[
            identified_collection_df.role_count == role_count_maxes]
        for role in range(1, 6):
            split_by_role_and_save(collection_name, identified_collection_df,
                                   role)
        
    return
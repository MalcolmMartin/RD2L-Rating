'''
StratzToGo Game Evaluation
'''

import pandas as pd
import numpy as np
from Point_Allocation import *

def benchmark_pp_advantage_points(column, min_point_level, max_point_level):
    # Assign advantage points coming from benchmarked percentile vs team mean
    column_mean = column.mean()
    advantage_points = \
        (column - column_mean - min_point_level) / \
        (max_point_level - min_point_level)
    advantage_points = np.clip(advantage_points, 0, 1)
    return advantage_points

def benchmark_advantage_points(column, min_point_level, max_point_level):
    # Assign advantage points coming from benchmarked percentile
    advantage_points = \
        (column - min_point_level) / (max_point_level - min_point_level)
    advantage_points = np.clip(advantage_points, 0, 1)
    return advantage_points

def calculate_utility_advantage(team_df):
    # Utility Advantage
    # TODO: only apply to heroes that actually do these things
    # 0 points awarded for 10th percentile, 20pp below
    min_hh_percentiles = [.1, -.2]
    min_stun_percentiles = [.1, -.2]
    # Max points awarded for 90th percentile, 20pp above
    max_hh_percentiles = [.9, .2]
    max_stun_percentiles = [.9, .2]
    
    # Hero Healing
    team_df = calculate_benchmark_advantages(
        team_df, 'utility', 'hh', 'hero_healing_per_min',
        min_hh_percentiles, max_hh_percentiles)
    
    # Stuns
    team_df = calculate_benchmark_advantages(
        team_df, 'utility', 'stun', 'stuns_per_min',
        min_stun_percentiles, max_stun_percentiles)
    
    return team_df

def calculate_tower_damage_advantage(team_df):
    # Tower Damage Advantage
    # 0 points awarded for 10th percentile, 20pp below
    min_td_percentiles = [.1, -.2]
    # Max points awarded for 90th percentile, 20pp above
    max_td_percentiles = [.9, .2]
    
    # Tower Damage
    team_df = calculate_benchmark_advantages(
        team_df, 'td', 'td', 'tower_damage',
        min_td_percentiles, max_td_percentiles)
    
    return team_df

def calculate_farm_advantage(team_df):
    # Farm Advantage
    # 0 points awarded for 35% hero/lane average,
    # 10% below expected, 35% hero/lane average,
    # 10% below expected 10th percentile, 20pp below
    min_gpm_average = -.65
    min_gpm_ratio_share = -.9
    min_xpm_average = -.65
    min_xpm_ratio_share = -.9
    min_lh_percentiles = [.1, -.2]
    # Max points awarded for 200% hero/lane average,
    # 15% above expected, 200% hero/lane average,
    # 15% above expected, 90th percentile, 20pp above
    max_gpm_average = 2
    max_gpm_ratio_share = 1.15
    max_xpm_average = 2
    max_xpm_ratio_share = 1.15
    max_lh_percentiles = [.9, .2]
    
    # Calculate actual vs expected gpm points
    gpm_advantage_points = (team_df['benchmarks.gold_per_min.raw'] + min_gpm_average *
                            team_df['hero_lane_gpm']) / \
                            ((max_gpm_average + min_gpm_average) *
                             team_df['hero_lane_gpm'])
    gpm_advantage_points = np.clip(gpm_advantage_points, 0, 1)
    
    # Calculate expected gpm ratios
    team_expected_total_gpm = team_df['hero_lane_gpm'].sum()
    team_df['expected_gpm_ratio'] = team_df["hero_lane_gpm"] / \
        team_expected_total_gpm
    
    # Calculate actual gpm ratios (maybe change to average of individual gpm vs team gpm)
    team_total_gpm = team_df['benchmarks.gold_per_min.raw'].sum()
    team_df["gpm_ratio"] = team_df["benchmarks.gold_per_min.raw"] / team_total_gpm

    # Calculate actual vs expected gpm ratio points
    gpm_ratio_advantage_points = (team_df['gpm_ratio'] + min_gpm_ratio_share * 
                                  team_df['expected_gpm_ratio']) / \
                                  ((max_gpm_ratio_share + min_gpm_ratio_share) *
                                   team_df['expected_gpm_ratio'])
    gpm_ratio_advantage_points = np.clip(gpm_ratio_advantage_points, 0, 1)
    
    # Calculate actual vs expected xpm points
    xpm_advantage_points = (team_df['benchmarks.xp_per_min.raw'] + min_xpm_average *
                            team_df['hero_lane_xpm']) / \
                            ((max_xpm_average + min_xpm_average) *
                             team_df['hero_lane_xpm'])
    xpm_advantage_points = np.clip(xpm_advantage_points, 0, 1)
    
    # Calculate expected xpm ratios
    team_expected_total_xpm = team_df['hero_lane_xpm'].sum()
    team_df['expected_xpm_ratio'] = team_df["hero_lane_xpm"] / \
        team_expected_total_xpm
    
    # Calculate actual gpm ratios (maybe change to average of individual gpm vs team gpm)
    team_total_gpm = team_df['benchmarks.xp_per_min.raw'].sum()
    team_df["xpm_ratio"] = team_df["benchmarks.xp_per_min.raw"] / team_total_gpm

    # Calculate actual vs expected gpm ratio points
    xpm_ratio_advantage_points = (team_df['xpm_ratio'] + min_xpm_ratio_share * 
                                  team_df['expected_xpm_ratio']) / \
                                  ((max_xpm_ratio_share + min_xpm_ratio_share) *
                                   team_df['expected_xpm_ratio'])
    xpm_ratio_advantage_points = np.clip(xpm_ratio_advantage_points, 0, 1)
    
    # Add to farm advantage
    team_df["farm_advantage"] += \
        point_dict['gpm_vs_average'] * gpm_advantage_points + \
        point_dict['gpm_vs_expected_ratio'] * gpm_ratio_advantage_points + \
        point_dict['xpm_vs_average'] * xpm_advantage_points + \
        point_dict['xpm_vs_expected_ratio'] * xpm_ratio_advantage_points
    
    # Last Hits
    team_df = calculate_benchmark_advantages(
        team_df, 'farm', 'lh', 'last_hits_per_min',
        min_lh_percentiles, max_lh_percentiles)
    
    return team_df

def calculate_hero_damage_advantage(team_df):
    # Hero Damage Advantage
    # 0 points awarded for 10th percentile, 20pp below
    min_hd_percentiles = [.1, -.2]
    # Max points awarded for 90th percentile, 20pp above
    max_hd_percentiles = [.9, .2]
    
    # Hero damage percentile and percentile vs median points
    team_df = calculate_benchmark_advantages(
        team_df, 'hd', 'hd', 'hero_damage_per_min',
        min_hd_percentiles, max_hd_percentiles)
    
    return team_df

def calculate_benchmark_advantages(
        team_df, adv_type, stat_type,
        bench_type, min_percentiles, max_percentiles):
    # iterate for absolute percentile and for percentile relative to team mean
    minor_cats = ['', '_mean']
    func_list = [benchmark_advantage_points, benchmark_pp_advantage_points]
    
    for func, minor_cat, min_per, max_per in zip(
        func_list, minor_cats, min_percentiles, max_percentiles):
        team_df[adv_type + '_advantage'] += \
            point_dict[stat_type + '_percentile' + minor_cat] * \
            func(team_df['benchmarks.' + bench_type + '.pct'], min_per, max_per)
    
    return team_df
    
def calculate_combat_advantage(team_df):
    # Combat Advantage
    # Compare KDA directly to lane and hero stats from Ala/Dotabuff
    # 0 points awarded for 35% hero/lane average,
    # 10% below expected, 50% below median
    # TODO: equations work, find fair min/max values
    min_kda_average = -.65
    min_kda_ratio_share = -.9
    min_ka_advantage = -.5
    # Max points awarded for 200% hero/lane average,
    # 15% above expected, 50% above median
    max_kda_average = 2
    max_kda_ratio_share = 1.15
    max_ka_advantage = 1.5
    
    # Calculate actual player kda
    team_df["ka"] = team_df["kills"] + team_df["assists"]
    team_df["kda"] = team_df["ka"] / np.maximum(team_df["deaths"], 1)
    
    # Calculate actual vs expected kda points
    kda_advantage_points = (team_df['kda'] + min_kda_average *
                            team_df['hero_lane_kda']) / \
                            ((max_kda_average + min_kda_average) *
                             team_df['hero_lane_kda'])
    kda_advantage_points = np.clip(kda_advantage_points, 0, 1)
    
    # Calculate expected kda ratios
    team_expected_total_kda = team_df['hero_lane_kda'].sum()
    team_df['expected_kda_ratio'] = team_df["hero_lane_kda"] / \
        team_expected_total_kda
    
    # Calculate actual kda ratios (maybe change to average of individual kda vs team kda)
    team_total_kda = (team_df["kills"].sum() + 
                      team_df["assists"].sum()) / \
                      np.maximum(team_df["deaths"].sum(), 1)
    team_df["kda_ratio"] = team_df["kda"] / team_total_kda

    # Calculate actual vs expected kda ratio points
    kda_ratio_advantage_points = (team_df['kda_ratio'] + min_kda_ratio_share * 
                                  team_df['expected_kda_ratio']) / \
                                  ((max_kda_ratio_share + min_kda_ratio_share) *
                                   team_df['expected_kda_ratio'])
    kda_ratio_advantage_points = np.clip(kda_ratio_advantage_points, 0, 1)

    # Calculate kill-assist participation points
    team_median_kills_assists = team_df["ka"].median()
    team_kp_advantage_points = (team_df["ka"] + min_ka_advantage * 
                                team_median_kills_assists) / \
                                ((max_ka_advantage + min_ka_advantage) *
                                 team_median_kills_assists)
    team_kp_advantage_points = np.clip(team_kp_advantage_points, 0, 1)
    
    team_df["combat_advantage"] += \
        point_dict['kda_hero_lane_average'] * kda_advantage_points + \
        point_dict['kda_ratio_vs_expected'] * kda_ratio_advantage_points + \
        point_dict['kill_assist_participation'] * team_kp_advantage_points        
    
    return team_df

def calculate_game_advantages(match_data):
    # List of all advantage functions
    func_list = [calculate_combat_advantage, calculate_hero_damage_advantage,
                 calculate_farm_advantage, calculate_tower_damage_advantage,
                 calculate_utility_advantage]
    
    # Split into team dataframes
    radiant = match_data[match_data['isRadiant'] == True]
    dire = match_data[match_data['isRadiant'] == False]
    
    # Iterate through all functions needed to evaluate advantage
    for func in func_list:
        radiant = func(radiant)
        dire = func(dire)
    
    # Concatenate both teams into a single dataframe:
    processed_match_data = pd.concat([radiant, dire])
    
    return processed_match_data
'''
StratzToGo Laning Evaluation
'''

import pandas as pd
import numpy as np
from Point_Allocation import point_dict

minute_categories = ['gold_5', 'xp_5', 'lh_5', 'dn_5',
                     'gold_10', 'xp_10', 'lh_10', 'dn_10']

def laning_advantage(radiant, dire, available_points, max_advantage):
    return available_points * np.clip((radiant - dire) / max_advantage, -1, 1)

def calculate_radiant_lane_advantage(radiant, dire):
    # TODO: Weigh cores heavier than supports in same lane
    # 5 minute max/0 points awarded for
    # 1000 nw, 750 xp, 15 lh and 15 dn advantage/disadvantage
    # 10 minute max/0 points awarded for
    # 2500 nw, 2000 xp, 35 lh and 25 dn advantage/disadvantage
    max_advantages = [1000, 750, 15, 15, 2500, 2000, 35, 25]
    
    # Get the advantage points relating to the laning indicators
    lane_advantage = 0
    for min_cat, max_adv in zip(minute_categories, max_advantages):
        num_radiant_laners = len(radiant.index)
        num_dire_laners = len(dire.index)
        if num_radiant_laners == num_dire_laners:
            radiant_average = radiant[min_cat].mean()
            dire_average = dire[min_cat].mean()
        elif num_radiant_laners > num_dire_laners:
            radiant_average = radiant[min_cat].mean()
            dire_average = (dire[min_cat].mean() * num_dire_laners) / num_radiant_laners
            dire_average += (dire['support_' + min_cat].mean() * (num_radiant_laners - num_dire_laners)) / num_radiant_laners
        else:
            print(radiant['hero_name'])
            print(min_cat)
            print(radiant['support_' + min_cat])
            radiant_average = (radiant[min_cat].mean() * num_radiant_laners) / num_dire_laners
            radiant_average += (radiant['support_' + min_cat].mean() * (num_dire_laners - num_radiant_laners)) / num_dire_laners
            dire_average = dire[min_cat].mean()
            print(radiant_average)
            print(dire_average)
        
        lane_advantage += laning_advantage(
            radiant_average, dire_average,
            point_dict['laning_' + min_cat], max_adv)
    
    return lane_advantage

def calculate_laning_advantage(lanes_dict):
    # Max points available across all categories is 25
    # with the max points per category given
    # Only +12.5/-12.5 across all categories is necessary
    # for the full/zero points in the laning stage
    
    for lane in ['bot', 'mid', 'top']:
        radiant_lane_advantage = \
            calculate_radiant_lane_advantage(
                lanes_dict['radiant_' + lane], lanes_dict['dire_' + lane])
        lanes_dict['radiant_' + lane]["lane_advantage"] += \
            radiant_lane_advantage
        lanes_dict['dire_' + lane]["lane_advantage"] -= radiant_lane_advantage
    
    # Concatenate all the lanes into a single dataframe
    laning_data = pd.concat(list(lanes_dict.values()))
    
    # Apply the positive/negative advantage to the midpoint
    laning_points = 0
    for min_cat in minute_categories:
        laning_points += point_dict['laning_' + min_cat]
    laning_data['lane_advantage'] /= 2
    laning_data['lane_advantage'] += laning_points / 2
    laning_data['lane_advantage'] = \
        np.clip(laning_data['lane_advantage'], 0, laning_points)
    
    return laning_data

def add_roles(lanes_dict):
    # Assign farming role
    # TODO: Handle core/support lane swaps
    # Assign core of each lane to highest last hits
    # safelane core is 1 and offlane core is 3
    lanes = ['radiant_bot', 'radiant_mid', 'radiant_top',
             'dire_bot', 'dire_mid', 'dire_top']
    roles = [1, 2, 3, 3, 2, 1]
    
    for lane, role in zip(lanes, roles):
        lanes_dict[lane].loc[
            lanes_dict[lane]["benchmarks.lhten.raw"].idxmax(), "role"] = role
    
    # TODO: handle having a roamer configuration
    # Assign supports
    # 4 is in offlane, 5 in safe lane
    # 4 has more lh at 10 than 5 in a trilane
    
    # Safe lane supports
    for lane in ['radiant_bot', 'dire_top']:
        if len(lanes_dict[lane].index) != 1:
            lanes_dict[lane].loc[
                lanes_dict[lane]["benchmarks.lhten.raw"].idxmin(), "role"] = 5
        if len(lanes_dict[lane].index) == 3:
            lanes_dict[lane].loc[
                lanes_dict[lane]["role"]=="", "role"] = 4
    
    # Off lane supports
    for lane in ['radiant_top', 'dire_bot']:
        if len(lanes_dict[lane].index) == 2:
            lanes_dict[lane].loc[
                lanes_dict[lane]["benchmarks.lhten.raw"].idxmin(), "role"] = 4
        elif len(lanes_dict[lane].index) == 3:
            lanes_dict[lane].loc[
                lanes_dict[lane]["benchmarks.lhten.raw"].idxmin(), "role"] = 5
            #lanes_dict[lane].loc[
            #    lanes_dict[lane]["role"]=="", lanes_dict[lane]["role"]] = 4
            lanes_dict[lane].loc[
                lanes_dict[lane]["role"]=="", "role"] = 4
    
    # Mid lane supports
    for team in ['radiant', 'dire']:
        used_roles = np.concatenate(
                [lanes_dict[team + '_bot']['role'].unique(),
                 lanes_dict[team + '_top']['role'].unique()])
        if len(lanes_dict[team + '_mid'].index) == 3:
            lanes_dict[team + '_mid'].loc[
                lanes_dict[team + '_mid']["benchmarks.lhten.raw"].idxmin(), \
                "role"] = 5
            lanes_dict[team + '_mid'].loc[
                lanes_dict[team + '_mid']["role"]=="",\
                lanes_dict[team + '_mid']["role"]] = 4
        elif len(lanes_dict[team + '_mid'].index) == 2:
            lanes_dict[team + '_mid'].loc[
                lanes_dict[team + '_mid']["role"]=="",\
                lanes_dict[team + '_mid']["role"]] = \
                ({4, 5} - set(used_roles)).pop()
                
    # TODO: Come up with a better solution for lane advantage for uneven lanes
    # Must have 1-5 assigned
    # Support and Core averages for all categories
    # Sum all categories using the support/core classification
    for team in ['radiant', 'dire']:
        for lane in ['_bot', '_mid', '_top']:
            for category in minute_categories:
                lanes_dict[team + '_bot']['support_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 4) | (lanes_dict[team + lane].role == 5)][category].sum()
                lanes_dict[team + '_mid']['support_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 4) | (lanes_dict[team + lane].role == 5)][category].sum()
                lanes_dict[team + '_top']['support_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 4) | (lanes_dict[team + lane].role == 5)][category].sum()
                    
                lanes_dict[team + '_bot']['core_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 1) | (lanes_dict[team + lane].role == 2) | (lanes_dict[team + lane].role == 3)][category].sum()
                lanes_dict[team + '_mid']['core_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 1) | (lanes_dict[team + lane].role == 2) | (lanes_dict[team + lane].role == 3)][category].sum()
                lanes_dict[team + '_top']['core_' + category] += \
                    (lanes_dict[team + lane])[(lanes_dict[team + lane].role == 1) | (lanes_dict[team + lane].role == 2) | (lanes_dict[team + lane].role == 3)][category].sum()
    
    # Average by dividing by 3 for cores and 2 for supports
    for team in ['radiant', 'dire']:
        for lane in ['_bot', '_mid', '_top']:
            for category in ['gold', 'xp', 'lh', 'dn']:
                lanes_dict[team + lane]['core_' + category + '_5'] /= 3
                lanes_dict[team + lane]['core_' + category + '_10'] /= 3
                lanes_dict[team + lane]['support_' + category + '_5'] /= 2
                lanes_dict[team + lane]['support_' + category + '_10'] /= 2
    
    
    
    return lanes_dict
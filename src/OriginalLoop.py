from pandas.core.frame import DataFrame
import requests
import pandas
import csv
import json
from bs4 import BeautifulSoup
import math

def makestats(lane):
    r = requests.get('https://www.dotabuff.com/heroes/lanes?lane='+lane, headers={'user-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'lxml')
    soup.find_all(class_="sortable")

    # #Processing table w/ BS 
    table = soup ('table')[0]
    headers = [th.text for th in table ('th')] #skipping garbage to grab all the text header guys
    rows = [x[1:] for x in [ [ td.text for td in tr('td') ] for tr in table.tbody('tr') ]]


    stats   = [ dict(zip(headers, row)) for row in rows ]
    #making dictionary then exporting it to json

    stats_dataframe = pandas.concat((pandas.json_normalize(d) for d in stats), axis=0)
    #stats_dataframe.to_csv(lane+'Stats.csv', index=False, encoding='utf-8')

    hero_ids = pandas.read_csv("Hero_Ids.csv")

    #print (hero_ids, stats_dataframe)
    #read all the rows in hero_ids and then see if stats dataframe has the hero and if it doesnt then add a placeholder 
    #print(stats_dataframe)
    for index, row in hero_ids.iterrows():
        #print(row ['hero_id'], row['hero_name'])
        if not stats_dataframe['Hero'].str.contains(row['hero_name']).any():
            # a_row = pandas.Series([row['hero_name'],'a', 'b', 'c', 'd', 'e'])
            # row_df = pandas.DataFrame([a_row])
            #stats_dataframe = pandas.concat([row_df, stats_dataframe], ignore_index=True)
            stats_dataframe = stats_dataframe.append({'Hero' : row['hero_name']} , ignore_index=True)

    return(stats_dataframe)

def get_dotabuff_hero_lane_data():
    #adding an extra column for lanes - ordering lanes to match up with positions 
    lanes = ['safe', 'mid', 'off', 'off', 'safe', 'jungle', 'roaming']
    positions = [1, 2, 3, 4, 5, 6, 7]

    statsbylane  = pandas.DataFrame()
    for lane, position in zip(lanes, positions):
        test = makestats(lane)
        df = pandas.DataFrame(test)
        df['Roles'] = position
        statsbylane = pandas.concat([statsbylane, test])

    #convert columns to non-percentage FLOATy bOIS
    statsbylane['Presence'] = statsbylane['Presence'].str.rstrip('%').astype('float') / 100.0
    statsbylane['Win Rate'] = statsbylane['Win Rate'].str.rstrip('%').astype('float') / 100.0
    statsbylane['KDA Ratio'] = statsbylane['KDA Ratio'].astype('float')
    statsbylane['GPM'] = statsbylane['GPM'].astype('float')
    statsbylane['XPM'] = statsbylane['XPM'].astype('float')

    for index, row in statsbylane.iterrows():
        if math.isnan(row['Presence']):
            statsbylane.at[index, 'Presence'] = 0
            statsbylane.at[index, 'Win Rate'] = statsbylane[statsbylane.Hero == row['Hero']]['Win Rate'].mean()
            statsbylane.at[index, 'KDA Ratio'] = statsbylane[statsbylane.Hero == row['Hero']]['KDA Ratio'].mean()
            statsbylane.at[index, 'GPM'] = statsbylane[statsbylane.Hero == row['Hero']]['GPM'].mean()
            statsbylane.at[index, 'XPM'] = statsbylane[statsbylane.Hero == row['Hero']]['XPM'].mean()

    statsbylane.to_csv('statsbylane.csv', index=False, encoding='utf-8')


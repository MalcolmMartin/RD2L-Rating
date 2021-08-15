import requests
import pandas
import csv
import json
from bs4 import BeautifulSoup



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

    return(stats_dataframe)

statsbylane  = pandas.DataFrame()
lanes = ['off', 'mid', 'safe', 'jungle', 'roaming']
for lane in lanes:
    test = makestats(lane)
    df = pandas.DataFrame(test)
    df['Roles'] = lane

    statsbylane = pandas.concat([statsbylane, test])
    #print (df)


print(statsbylane)
statsbylane.to_csv('statsbylane.csv', index=False, encoding='utf-8')





# concatenate dataframes (the lanes basically) 
# - pull lanes out of loop, then make em at the end 
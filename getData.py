#coding:utf-8
import os
import json
import requests
import csv
import pandas as pd

def get(filepath,eventNumber,eventType,showComplete=True):
    '''this Defines the Data which need to return to alive
    :filepath: *str ~ the specific path you want to insert file into
    :eventNumber: *int ~ a number which event you want to get
    :eventType: *int ~ for 0-2 is 100/1000/2000
    :showComplete: *bool ~ see the last phrase
    :return: a csv file which save to specific position
    this can also trigs a output of isDownloadComplete, if not set 4th parameter to *False
    '''
    hd={'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    #the web api which returns the specific EventData
    url1='http://bandoriapi.cn//Query/Event/eventData/'+str(eventNumber) 
    eventData=requests.get(url1,headers=hd).text
    eventDict=json.loads(eventData)
    eventName=eventDict['rS']['eventName'][3]
    eventStart=int(eventDict['rS']['startAt'][3])/1000
    eventEnd=int(eventDict['rS']['endAt'][3])/1000
    timediff=eventEnd-eventStart
    #tier 0 1 2
    url2="https://bestdori.com/api/tracker/data?server=3&event="+str(eventNumber)+"&tier="+str(eventType)
    epData = requests.get(url2,headers=hd).text
    epDict=(json.loads(epData))['cutoffs']
    epjson=json.dumps(epDict)

    df = pd.read_json(epjson,orient='records',typ='frame')
    df.eval('pct=(((time/1000)-'+str(eventStart)+")/"+str(timediff)+')*100',inplace=True)
    df.eval('val=ep',inplace=True)
    df.drop(labels='time',axis=1, inplace=True)
    df.drop(labels='ep',axis=1, inplace=True)
    df.drop_duplicates(keep='first',inplace=True)
    df['pct'] = round(df['pct'],3)
    df.pct[df['pct']>=100]=float(100)

    if not os.path.exists(filepath):
        os.mkdir(filepath)

    f = open(filepath+"bd_e"+str(eventNumber)+"t"+str(eventType)+".json",mode='w')
    df.to_json(f,'records')
    f.close()

    if showComplete:
        print("Json Write Complete!",str(eventNumber),"TypeOn:",str(eventType),"->")

    return df

    
#coding:utf-8
import os
import json
import requests
import csv
import pandas as pd

def get(filepath,eventNumber,rankType,regionType=3,showComplete=True):
    '''this Defines the Data which need to return to alive
    :filepath: *str ~ the specific path you want to insert file into
    :eventNumber: *int ~ a number which event you want to get
    :rankType: *int ~ for 0-2 is 100/1000/2000
    :showComplete: *bool ~ see the last phrase
    :return: a csv file which save to specific position
    this can also trigs a output of isDownloadComplete, if not set 4th parameter to *False
    '''
    hd={'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
    url='http://bandoriapi.cn/Query/Event/eventDataTracker/'+str(regionType)+'/'+str(eventNumber)+'/'+str(rankType)
    
    eventData=requests.get(url,headers=hd).text
    eventDict=json.loads(eventData)
    eventName=eventDict['Data']['eventName'][3]
    eventStart=int(eventDict['Data']['startAt'][3])/1000
    eventEnd=int(eventDict['Data']['endAt'][3])/1000
    timediff=eventEnd-eventStart
    epDict0=(json.loads(eventData))['rS']['cutoffs']
    
    epDict=[]
    for itemcount in range(0,len(epDict0)):

        try:
            if len(epDict0)>3 and 1<= itemcount<(len(epDict0)-1):

                pt1=int(epDict0[itemcount-1]['ep'])
                pt2=int(epDict0[itemcount]['ep'])
                pt3=int(epDict0[itemcount+1]['ep'])
                if pt1<pt2 and pt2>pt3:
                    pass
                else:
                    epDict.append(epDict0[itemcount])
            else:
                epDict.append(epDict0[itemcount])
            
        except Exception as e:
            print(e)

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

    f = open(filepath+"bd.json",mode='w')
    df.to_json(f,'records')
    f.close()

    if showComplete:
        print("Bestdori Json Write Complete!",str(eventNumber),"TypeOn:",str(rankType),"->")

    return df

    
import os
import DataRef
import GraphDraw
import time,datetime

#os: NT for testing; Linux for operating

if os.name=='nt':
    basePath='D:/RinkoPredict/curevent/'
else:
    basePath='/data/web/api/ycxcore/'
    
areacode=0    #country Code
enum=117             


while True:
    
    #make sure of Dir is create
    if not os.path.exists(basePath):
        os.mkdir(basePath)
    if not os.path.exists(basePath+str(areacode)):
        os.mkdir(basePath+str(areacode))

    try:
        DataRef.GetDataStorage(basePath,areacode,enum)            #make sure that we've already storage the file
    except Exception as e1:
        print('Analyse Fail!',e1)

    print('操作完成时间 区服*->',areacode,'<-',datetime.datetime.fromtimestamp(time.time()).strftime("%m/%d %H:%M:%S"))
   
    if os.name=='nt':   
        break
    else: 
        time.sleep(180)
        os.system('clear')

import os
import DataRef
import GraphDraw
import time
imgbasePath='D:/asd/now/'
basePath='D:/asd/'

#imgbasePath='/root/web/rinkoapi/curevent/'
#basePath='/root/web/rinkoapi/ycxcore/'

areacode=3          #country Code
TogglePara = True  #if PredNow please to change to True
#test only
Bnum=70          #eventNumber
    
    
#make sure of Dir is create
if not os.path.exists(imgbasePath):
    os.mkdir(imgbasePath)
if not os.path.exists(basePath):
    os.mkdir(basePath)
if not os.path.exists(basePath+str(areacode)):
    os.mkdir(basePath+str(areacode))

while True:
    try:
        DataRef.GetDataStorage(basePath,areacode,TogglePara,Bnum)             #make sure that we've already storage the file
        GraphDraw.GetDataPic(areacode,imgbasePath,basePath,TogglePara,Bnum)   #use file to Pic
    except:
        print('FAIL')
    time.sleep(300)
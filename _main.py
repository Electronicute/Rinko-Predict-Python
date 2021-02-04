import os
import DataRef
import GraphDraw
import time,datetime
if os.name=='nt':
    imgbasePath='D:/asd/now/'
    basePath='D:/asd/'
else:

    imgbasePath='/data/web/api/curevent/'
    basePath='/data/web/api/ycxcore/'
    
areacode=3          
#country Code
TogglePara = True   
#if PredNow please to change to True
Bnum=1              
#eventNumber,NO-use if above is True
    
    
#make sure of Dir is create
if not os.path.exists(imgbasePath):
    os.mkdir(imgbasePath)
if not os.path.exists(basePath):
    os.mkdir(basePath)
if not os.path.exists(basePath+str(areacode)):
    os.mkdir(basePath+str(areacode))

while True:
    for x in range(0,4):
        try:
            DataRef.GetDataStorage(basePath,x,TogglePara,Bnum)             #make sure that we've already storage the file
        except Exception as e1:
            print('Analyse Fail!',e1)

        try:
            GraphDraw.GetDataPic(x,imgbasePath,basePath,TogglePara,Bnum)   #use file to Pic
        except Exception as e2:
            print('Draw Fail!',e2)

        print('操作完成时间 区服*->',x,'<-',datetime.datetime.fromtimestamp(time.time()).strftime("%m/%d %H:%M:%S"))
   
    if os.name=='nt':
        break
    else: 
        time.sleep(180)
        os.system('clear')

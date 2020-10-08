# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt
import json
import datetime,time
import requests
import PIL.Image as Image
import PIL.ImageFont as ImageFont
import PIL.ImageDraw as ImageDraw
import shutil

def main(eventNumber,rankType,areacode,basePath,JsonPath):
    
    def timestamp(x): #换算时间戳到天数    
        dateArray = datetime.datetime.fromtimestamp(x)
        day =int(dateArray.strftime("%d"))
        month=int(dateArray.strftime("%m"))
        return day,month
    def timestamp_full(x):#换算时间戳到具体时间
        dateArray = datetime.datetime.fromtimestamp(x)
        return dateArray.strftime("%m/%d %H:%M:%S")
    
    def basicGet(eventNumber,rankType):
        hd={'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
        url='http://bandoriapi.cn/Query/Event/eventDataTracker/'+str(areacode)+'/'+str(eventNumber)+'/'+str(rankType)
        eventData=requests.get(url,headers=hd).text
        eventDict=json.loads(eventData)
        eventName=eventDict['Data']['eventName'][3]
        eventStart=int(eventDict['Data']['startAt'][3])/1000
        eventEnd=int(eventDict['Data']['endAt'][3])/1000
        return eventName,eventStart,eventEnd
        
    def dataTrans(eventNumber,AreaCode,enum,etp):
        jsondir=JsonPath+str(AreaCode)+"/"+"e"+str(enum)+"/"+"t"+str(etp)+"/"+"event.json" #此处要改！！
        predictJson=open(jsondir)
        preDict=json.load(predictJson)
        pctList=[]
        ptList=[]
        slpList=[]
        ufinList=[]
        finList=[]
        bfinList=[]
        for items in preDict:
            pctList.append(items['PCT'])
            ptList.append(items['REALY'])
            slpList.append(items['SLPSLP'])
            ufinList.append(items['UFIN'])
            finList.append(items['FIN'])
            bfinList.append(items['BFIN'])
        return pctList,ptList,slpList,ufinList,finList,bfinList
    
    def graphDraw(pctList,ptList,slpList,ufinList,finList,bfinList):    
        plt.rcParams['savefig.dpi'] = 600
        plt.rcParams['figure.dpi'] = 600
        ax=plt.figure().add_subplot(111)
        plt.rcParams['font.sans-serif']=['DengXian']
        plt.grid(True)
        plt.ticklabel_format(style='plain', axis='y')
        plt.xlim([-19,103])
        ax.yaxis.tick_right()
        plt.xlabel('进度(%)')
    
        plt.plot(pctList,ptList,marker='o')
        plt.text(pctList[-1],ptList[-1]*0.9,'%.0f'%ptList[-1],ha = 'center',va = 'bottom')  
        progress=(time.time()-eventStart)/(eventEnd-eventStart)*100
        if progress>100:
            progress=100
            
        legendList=['实时分数线']
        if finList[-1]!=None:
            plt.vlines(progress,0,finList[-1]*1.2,color='green',ls='--')
            plt.plot(pctList,finList,marker='*',ls='--',color='red')
            plt.text(pctList[-1],finList[-1]*1.05,'%.0f'%finList[-1],ha = 'center',va = 'bottom')    
            legendList.append('预测最终分数')
        else:
            plt.vlines(progress,0,ptList[-1]*1.2,color='green',ls='--')
        
        legendList.append('目前进度')    
        plt.legend(legendList,loc='lower right')    
        plt.savefig('resources/chart.png', dpi=600, bbox_inches='tight')
        plt.close()  
        
        fig, ax = plt.subplots()
        fig.patch.set_alpha(0.) 
        plt.pie([100-progress,progress],wedgeprops=dict(width=0.1))
        fig.savefig('resources/ring.png',dpi=450, transparent=True, bbox_inches='tight')
        plt.close() 
        
        if  pctList[-1]>=85:
            plt.figure().add_subplot(111)
            plt.ticklabel_format(style='plain', axis='y')
            plt.xlabel('进度(%)')
            plt.grid(True)
            plt.title('分数线局部放大图')
            plt.plot(pctList[-5:],ptList[-5:])
            plt.scatter(pctList[-5:],ufinList[-5:],color='red',marker='*')
            plt.scatter(pctList[-5:],finList[-5:],color='orange',marker='o')
            plt.scatter(pctList[-5:],bfinList[-5:],color='green',marker='*')
            plt.text(pctList[-1],ufinList[-1]*1.02,'%.0f'%finList[-1],ha = 'center',va = 'bottom')  
            plt.text(pctList[-1],finList[-1],'%.0f'%finList[-1],ha = 'center',va = 'bottom')    
            plt.text(pctList[-1],ptList[-1]*0.95,'%.0f'%ptList[-1],ha = 'center',va = 'bottom')  
            plt.legend(['实时分数线','预测分数线(均值)','预测分数线(上限)','校正点'],loc='upper left')
            plt.savefig('resources/Detailchart.png', dpi=600, bbox_inches='tight')
            plt.close()  
            able=1
        else:
            able=0   
        return able
    
    def picDraw(pctList,ptList,slpList,ufinList,finList,bfinList,eventName,eventStart,eventEnd,rankType,able,basePath):
        rankList=['[T 100]','[T1000]','[T2000]']
        rankList2=['e100','e1k','e2k']
        progress=int(((time.time()-eventStart)/(eventEnd-eventStart)*100))
        if progress>100:
            progress=100
        ptNow=str(ptList[-1])
        ptPredict=str('%.0f'%finList[-1])
        if ptPredict==None:
            ptPredict='--'
        endTime=timestamp_full(eventEnd)
        nowTime=timestamp_full(time.time())
        ptTimestamp=(pctList[-1])*0.01*(eventEnd-eventStart)+eventStart
        ptTime=timestamp_full(ptTimestamp)
        print('正在生成<',eventName,'>'+rankList[rankType]+'分数线信息')    
       
        im = Image.open("resources/background70.png")
        
        box=(75,500,3425,2810)
        chart1= Image.open('resources/chart.png')
        region = chart1
        region = region.resize((box[2] - box[0], box[3] - box[1]))
        im.paste(region, box)
        if able==1:
            box2= (75,500,1750,1690)
            chart2= Image.open('resources/Detailchart.png')
            region2 = chart2
            region2 = region2.resize((box2[2] - box2[0], box2[3] - box2[1]))
            im.paste(region2, box2)
        else:
            pass
        
        chart3= Image.open('resources/ring.png')
        region3 = chart3
        region3 = region3.resize((1449,1449))
        region3=region3.crop((180,180,1270,1270))
        box3=(30,2850,1120,3940)

        im.paste(region3,box3,region3)
        im=im.convert('RGBA')
        txt=Image.new('RGBA', im.size, (0,0,0,0))
        
        fnt=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 160)
        fnt2=ImageFont.truetype("resources/Helvetica Bold.ttf", 160) 
        fnt3=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 120)
        
        d=ImageDraw.Draw(txt) 
        titlex=1750-(len(eventName)+2)/2*160
        d.text((titlex,100),'《'+eventName+'》',font=fnt, fill=(0,0,0,255))
        d.text((3020,360),rankList[rankType],font=fnt3, fill=(0,0,0,255))
        d.text((400,3415),str(progress)+'%',font=fnt2, fill=(0,0,0,255))
        scorex1=3100-len(ptNow)/2*160
        scorex2=3100-len(ptPredict)/2*160
        d.text((scorex1,3100),ptNow,font=fnt2, fill=(0,0,0,255))
        d.text((scorex2,3690),ptPredict,font=fnt2, fill=(0,0,0,255))
        d.text((2480,3250),ptTime,font=fnt3, fill=(0,0,0,255))
        d.text((2480,3850),endTime,font=fnt3, fill=(0,0,0,255))
        d.text((1280,3750),nowTime,font=fnt3, fill=(0,0,0,255))
        
        out=Image.alpha_composite(im,txt)
        out=out.resize((1750,2500))
        filename=basePath+rankList2[rankType]+'.png'
        out.save(filename)

            
    def noptHandle(eventName,basePath,rankType=4):
        im = Image.open("resources/noPt70.png")
        txt=Image.new('RGBA', im.size, (0,0,0,0))
        fnt=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 50)
        fnt2=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 20)
        titlex=400-(len(eventName)+2)/2*50
        d=ImageDraw.Draw(txt) 
        d.text((titlex,100),'《'+eventName+'》',font=fnt, fill=(0,0,0,255))
        d.text((450,500),'制图时间：'+timestamp_full(time.time()),font=fnt2, fill=(0,0,0,255))
        out=Image.alpha_composite(im,txt)
        if rankType==4:
            for filename0 in ['e100.png','e1k.png','e2k.png']:
                filename=basePath+filename0
                out.save(filename)
        else:
            flist=['e100.png','e1k.png','e2k.png']
            filename=basePath+flist[rankType]
            out.save(filename)
    
    (eventName,eventStart,eventEnd)=basicGet(eventNumber,rankType)
    try:
        (pctList,ptList,slpList,ufinList,finList,bfinList)=dataTrans(eventNumber,areacode,eventNumber,rankType)
        if len(pctList)>=3:
            able=graphDraw(pctList,ptList,slpList,ufinList,finList,bfinList)
            picDraw(pctList,ptList,slpList,ufinList,finList,bfinList,eventName,eventStart,eventEnd,rankType,able,basePath)    
        else:
            noptHandle(eventName,basePath,rankType)
    except:
        noptHandle(eventName,basePath,rankType)

        
def nopicHandle(imgbasePath):
    for filename0 in ['e100.png','e1k.png','e2k.png']:
        filename=imgbasePath+filename0
        shutil.copyfile('resources/noevent.png', filename)

def GetDataPic(areacode,basePath,JsonPath,PredNow=True,Benum=0):
    '''this is the Main Core for Data Pic Print
    :basePath ~ which should be the Image's storage path
    :JsonPath ~ which indecate the Json file storage path
    :PredNow ~ which indecate of weather or not Predict Event Of now
        NOTICE this will change the behaviour of the function: 
        if this enable you MUST enter next few value
        :Benum is the event number that you want to check.
    '''
    if(PredNow):
        hd={'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
        url='http://bandoriapi.cn/Query/Event/eventNow/'+str(areacode)
        Data=requests.get(url,headers=hd).text
        Dict=json.loads(Data)
        enum=int(Dict['rS'][1:])
        if Dict['rS']!='N00':
            for typ in range(0,3):
                main(enum,typ,areacode,basePath,JsonPath)

        else:
            nopicHandle(basePath)
    else:
        for typ in range(0,3):
                main(Benum,typ,areacode,basePath,JsonPath)
    print('完成时间',datetime.datetime.fromtimestamp(time.time()).strftime("%m/%d %H:%M:%S"))





# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt
import json
import datetime,time
import requests,urllib
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
    
    def basicGet(eventNumber,rankType,areacode):
        hd={'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'}
        url='http://bandoriapi.cn/Query/Event/eventDataTracker/'+str(areacode)+'/'+str(eventNumber)+'/'+str(rankType)
        eventData=requests.get(url,headers=hd).text
        eventDict=json.loads(eventData)
        eventName=eventDict['Data']['eventName'][areacode]
        eventStart=int(eventDict['Data']['startAt'][areacode])/1000
        eventEnd=int(eventDict['Data']['endAt'][areacode])/1000
        
        #这里获取bannerTitle（临时）
        pic_filename='resources/'+str(eventNumber)+'title.png'
        if not os.path.exists(pic_filename):
            print('Downloading titleImage...')
            url2='http://bandoriapi.cn/Query/Event/eventGenData/'+str(eventNumber)+'/'+str(areacode)+'/assetBundleName'
            eventData=requests.get(url2,headers=hd).text
            eventDict=json.loads(eventData)
            assetName=eventDict["rS"]
            pic_url='https://bestdori.com/assets/cn/event/'+assetName+'/images_rip/logo.png'
            r=requests.get(pic_url,headers=hd)
            with open(pic_filename,"wb") as f:
                f.write(r.content)
            f.close()

        else:
            pass

        return eventName,eventStart,eventEnd

    def dataTrans(eventNumber,AreaCode,enum,etp):
        jsondir=JsonPath+str(AreaCode)+"/"+"e"+str(enum)+"/"+"t"+str(etp)+"/"+"event.json" 
        if not os.path.exists(jsondir):
            noptHandle(etp)
        else:
            predictJson=open(jsondir)
            preDict=json.load(predictJson)
            pctList=[]
            ptList=[]
            slpList=[]
            ufinList0=[]
            finList0=[]
            bfinList0=[]
            ufinList=[]
            finList=[]
            bfinList=[]
            predPct=[]
            for items in preDict:
                pctList.append(items['PCT'])
                ptList.append(items['REALY'])
                slpList.append(items['SLPSLP'])
                ufinList0.append(items['UFIN'])
                finList0.append(items['FIN'])
                bfinList0.append(items['BFIN'])
            for I in finList0:
                if I!=None:
                    itemNum=finList0.index(I)
                    predPct.append(pctList[itemNum])
                    finList.append(I)
                    ufinList.append(ufinList0[itemNum])
                    bfinList.append(bfinList0[itemNum])

            return pctList,ptList,slpList,ufinList,finList,bfinList,predPct
    
    def graphDraw(pctList,ptList,slpList,ufinList,finList,bfinList,predPct):    
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
            plt.plot(predPct,finList,marker='*',ls='--',color='red')
            plt.text(predPct[-1],finList[-1]*1.05,'%.0f'%finList[-1],ha = 'center',va = 'bottom')    
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
        
        if  len(pctList)>=5 and pctList[-3]>=90:
            plt.figure().add_subplot(111)
            plt.ticklabel_format(style='plain', axis='y')
            plt.xlabel('进度(%)')
            plt.grid(True)
            plt.title('分数线局部放大图')
            plt.plot(pctList[-5:],ptList[-5:])
            plt.scatter(pctList[-5:],ufinList[-5:],color='red',marker='*')
            plt.scatter(pctList[-5:],finList[-5:],color='orange',marker='o')
            plt.scatter(pctList[-5:],bfinList[-5:],color='green',marker='*')
            plt.text(pctList[-1],ufinList[-1]*1.02,'%.0f'%ufinList[-1],ha = 'center',va = 'bottom')  
            plt.text(pctList[-1],finList[-1],'%.0f'%finList[-1],ha = 'center',va = 'bottom')    
            plt.text(pctList[-1],ptList[-1]*0.95,'%.0f'%ptList[-1],ha = 'center',va = 'bottom')  
            plt.legend(['实时分数线','预测分数线(上限)','预测分数线(均值)','校正点'],loc='upper left')
            plt.savefig('resources/Detailchart.png', dpi=600, bbox_inches='tight')
            plt.close()  
            able=1
        else:
            able=0   
        return able



    def picDraw(pctList,ptList,slpList,ufinList,finList,bfinList,eventName,eventStart,eventEnd,rankType,able,basePath):
        rankList=['[TOP  100]','[TOP 1000]','[TOP 2000]']
        flist=['e100.png','e1k.png','e2k.png']
        progress=int(((time.time()-eventStart)/(eventEnd-eventStart)*100))
        if progress>100:
            progress=100
        ptNow=str(ptList[-1])
        ptPredict=finList[-1]
        if ptPredict==None:
            ptPredict='--'
            print('注意：当前最终点没有预测信息')
        else:
            ptPredict=str('%.0f'%finList[-1])
        endTime=timestamp_full(eventEnd)
        nowTime=timestamp_full(time.time())
        ptTimestamp=(pctList[-1])*0.01*(eventEnd-eventStart)+eventStart
        ptTime=timestamp_full(ptTimestamp)
        print('正在生成<',eventName,'>'+rankList[rankType]+'分数线图片')    
       
        im = Image.open("resources/backgroundNEO.png")
        
        box=(0,880,3500,3180)
        chart1= Image.open('resources/chart.png')
        region = chart1
        region = region.resize((box[2] - box[0], box[3] - box[1]))
        im.paste(region, box)
        if able==1:
            box2= (0,880,1680,2070)
            chart2= Image.open('resources/Detailchart.png')
            region2 = chart2
            region2 = region2.resize((box2[2] - box2[0], box2[3] - box2[1]))
            im.paste(region2, box2)
        else:
            pass
        
        chart3= Image.open('resources/ring.png')
        region3 = chart3
        region3 = region3.resize((1450,1450)) 
        region3=region3.crop((175,175,1280,1280))
        box3=(78,3290,933,4145)
        region3 = region3.resize((box3[2] - box3[0], box3[3] - box3[1]))
        im.paste(region3,box3,region3)

        titlepic=Image.open('resources/'+str(eventNumber)+'title.png')
        region4=titlepic
        box4=(222,77,1474,631)
        region4=region4.resize((box4[2] - box4[0], box4[3] - box4[1]))
        im.paste(region4,box4,region4)

        im=im.convert('RGBA')
        txt=Image.new('RGBA', im.size, (0,0,0,0))
        
        fnt=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 160)
        fnt2=ImageFont.truetype("resources/Helvetica Bold.ttf", 165) 
        fnt3=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 90)
        
        d=ImageDraw.Draw(txt) 
        
        d.text((1844,3200),rankList[rankType],font=fnt2, fill=(0,0,0,255))
        precentx=514-fnt2.getsize(str(progress)+'%')[0]/2

        d.text((precentx,3750),str(progress)+'%',font=fnt2, fill=(0,0,0,255))
        scorex1=2070-(fnt2.getsize(ptNow))[0]/2
        scorex2=2827-(fnt2.getsize(ptPredict))[0]/2
        d.text((scorex1,3435),ptNow,font=fnt2, fill=(255,0,0,255))
        d.text((scorex2,3840),ptPredict,font=fnt2, fill=(0,0,0,255))

        nowPredictpt='------'
        scorex3=1635-(fnt.getsize(nowPredictpt))[0]/2
        d.text((scorex3,3840),nowPredictpt,font=fnt, fill=(0,0,0,255))

        d.text((2480,3490),ptTime+"("+str(int(pctList[-1]))+"%)",font=fnt3, fill=(0,0,0,255))
        d.text((2510,4033),endTime,font=fnt3, fill=(0,0,0,255))
        d.text((1300,4033),nowTime,font=fnt3, fill=(0,0,0,255))
        
        out=Image.alpha_composite(im,txt)
        out=out.resize((1750,2500))
        filename=basePath+flist[rankType]
        out.save(filename)

            
    def noptHandle(eventName,basePath,rankType=4):
        im = Image.open("resources/noPt.png")
        im=im.convert('RGBA')
        txt=Image.new('RGBA', im.size, (0,0,0,0))
        fnt=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 50)
        fnt2=ImageFont.truetype("resources/HYZhengYuan-55W.ttf", 20)
        title='《'+eventName+'》'
        titlex=400-(fnt.getsize(title))[0]/2
        d=ImageDraw.Draw(txt) 
        d.text((titlex,100),title,font=fnt, fill=(0,0,0,255))
        d.text((450,500),'制图时间：'+timestamp_full(time.time()),font=fnt2, fill=(0,0,0,255))
        out=Image.alpha_composite(im,txt)
        flist=['e100.png','e1k.png','e2k.png']
        if rankType==4:
            for filename0 in flist:
                filename=basePath+filename0
                out.save(filename)
        else:
            filename=basePath+flist[rankType]
            out.save(filename)
    
    (eventName,eventStart,eventEnd)=basicGet(eventNumber,rankType,areacode)
    try:
        (pctList,ptList,slpList,ufinList,finList,bfinList,predPct)=dataTrans(eventNumber,areacode,eventNumber,rankType)
        if len(pctList)>=3:
            able=graphDraw(pctList,ptList,slpList,ufinList,finList,bfinList,predPct)
            picDraw(pctList,ptList,slpList,ufinList,finList,bfinList,eventName,eventStart,eventEnd,rankType,able,basePath)    
        else:
            noptHandle(eventName,basePath,rankType)
    except Exception as ex:
        noptHandle(eventName,basePath,rankType)
        print(ex)
       
        
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
   





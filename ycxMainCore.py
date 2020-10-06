"""system Import"""
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
"""custom APIs"""
import getData
import getPred
import outData

def __Main__RunPred(filepath,enum,etp,pred_Length=3,gamma_Threshold=1):
    '''this is the EntryPoint of the specific NLD_Core
    :filepath ~ a path of Content should be Save :like "D:/asd/"
        you must keep the last slash(/) to keep the code running
    :enum ~ it's the Event Number 
    :etp ~ it's EventType which is correspond to 0-2 is 100,1k,2k
    :pred_Length ~ is the corr of predict which the determinator of LLB
        this represent the LBSB (left Block Span Block)'s 
        RCPD (Rest Control Position Determinator)
        it's the determinator of whole predict
        don't change it if you don't konw what you're doing 
        please leave at 3-6
    :gamma_Threshold ~ is the Threshold of the final predict Threshold
        if you don't know what will happen please do not change it,
        as we test it's best to leave it at 1 or 2
    '''

    fp = filepath+"e"+str(enum)+"t"+str(etp)+"/"
    fir = pd.DataFrame()
    #getData using BAC and Bestdori Database
    fir = getData.get(fp,enum,etp)
    #predict Data
    mid = getPred.PreProcessData(fp,enum,etp,fir,pred_Length,gamma_Threshold,True) #middle ware of predict
    #Outpu Data
    outData.OutPut(fp,enum,etp,mid)
    return True

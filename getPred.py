import os
import math
import numpy as np
import statsmodels.api as sm
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def __REG(df,num,llb):
	'''this is DPRA's Regression Predict Model
	:df ~ [DataFrame] which contains the most LLB's DataFrame
	:num ~ [int] present number
	:llb ~ [int] most left' left block
	return DataFrame which contains
	PCT | RSQ | SLP | ICT | REGFIN
	'''

	#re-adapt the x,y
	x = np.array(df.pct).reshape((-1,1)) 	#get value x which is represent on "t" as percent to the proto-time
	y = np.array(df.val)					#get value y which is represent on "s" as number to the present-past score
	i = num-1								#get the total length (*Present District Postion)			

	#create Model and Assign it
	md = LinearRegression()		#create a model
	md = md.fit(x,y)			#insert a value

	#list result of RSQ Intercept and slope
	RSQ = np.around(md.score(x,y),4)
	SLP = np.around(md.intercept_,2)
	IRC = np.around(md.coef_,2)

	#try predict the next value and Final value
	last = np.array([100]).reshape((-1,1))		#last Value
	FINAL = md.predict(last)					#DPRA Pred
	PERCENT = df.pct[i]							#cali-percent

	#try to print out value
	result = pd.DataFrame([[float(PERCENT),float(RSQ),float(SLP),float(IRC),float(FINAL)]],\
		columns=["PCT","REGRSQ","REGSLP","REGICT","REGFIN"]).rename({0:""})
	return result

def __SLP(df):
	'''this is the DPRA-Slope analysis core
	:df		~ [DataFrame] 
	return DataFrame which contains
	PCT | SLPSLP | SLPFIN
	'''
	x = np.array(df.pct).reshape((-1,1))
	y = np.array(df.val)
	SLP = (y[-2]-y[-1])/(x[-2]-x[-1])
	TimeLapse = float(100-x[-1])
	FINAL = float(y[-1]) + (TimeLapse * SLP)
	PERCENT = x[-1]
	result = pd.DataFrame([[float(PERCENT),float(SLP),np.around(float(FINAL),2)]],\
		columns=["PCT","SLPSLP","SLPFIN"]).rename({0:""})
	return result

def ProcessDataUniquefiy(dfp):
	try:
		#caliV
		a = dfp.loc[(dfp["DIFF"]==0) & (dfp["PCT"]>=float(90))].head(1)
		b = dfp.loc[dfp["PCT"]>float(a["PCT"])].head(1)			#upper block of Method change
		c = dfp.loc[dfp["PCT"]>float(a["PCT"])].head(2).tail(1)	#lower block of Method change
		lpct = np.around(float(c["PCT"]),1)
		dx = np.around(float(abs(float(b["REGFIN"])-float(c["SLPFIN"]))),1)
		return pd.DataFrame([[dx,lpct]],columns=["dx","lpct"]).rename({0:""})
	except:
		return pd.DataFrame([[float(0),float(0)]],columns=["dx","lpct"]).rename({0:""})

def PreProcessData(filepath,enum,etp,df,pred_length=6,gamma_threshold=1,usefile=False):
	'''this is the Data Pre-Process Method. which using GCDS (gamma-CDS)
	:fileCSVpath : is the path that you configuate in the File
	:is the BIG event you need to import
	:pred_length ~int | number which defines how much Data should be process as time goes *
		if this value rises the data will be more accurate, but data will delay more time *
	:gamma_threshold ~int | this is the number of how your gamma will be rectifyed *
		beacuse there's negative value of gamma is gain much larger when not final yet *
	:return [a DataFrame of Final]
	'''
	if(usefile):
		df = pd.read_json(filepath+"bd_e"+str(enum)+"t"+str(etp)+".json", encoding='utf-8')

	pd.set_option('display.max_columns', None)			#define show all columns
	pd.set_option('display.max_rows', None)				#define show all columns
	pd.set_option('expand_frame_repr', False)			#defines to not re-adapt the columns
	pd.options.display.float_format = '{:.4f}'.format	#defines to show 2 dig of digt.

	#pre-define
	slppred = pd.DataFrame()
	regpred = pd.DataFrame()
	diffcol = pd.DataFrame()
	dfx = pd.DataFrame()
	
	#to regission pred
	for num in range(pred_length+1,len(df)+1):
		#Present Block : num
		#Total Block : len(df)
		#Present perCenTage : (1 - num//len(df))*len(df) 
		#LB Span Block : math.ceil((1 - int(df["0"][num-1])/df["0"][len(df)-1])*len(df))
		#Lower Linear Block : num - PCT (if<0 then,LLB=pred_length)
		try:
			LBSB = math.ceil((1 - float(df.pct[num-1])/df.pct[len(df)-1])*len(df))
			LLB = num-LBSB	
			if (LLB<=pred_length+1):
				LLB = pred_length-1	
			elif (LLB == num):
				LLB = num-1		
			else:
				LLB = num-LBSB	

			regx = __REG(df[LLB:num],num,LLB)
			regpred = regpred.append(regx ,ignore_index=True)
		except:
			continue

	#to Slope analysis
	for num in range(2,len(df)+1):
		try:
			slpx = __SLP(df[num-2:num])
			slppred = slppred.append(slpx ,ignore_index=True)
		except:
			continue

	#merge the dataframe
	df.rename(columns={"pct": "PCT", "val": "REALY"},inplace=True)
	dfx=pd.merge(df,slppred,how='outer')
	dfx=pd.merge(dfx,regpred,how='outer')
	dfx.eval('DIFF=abs(REGFIN-SLPFIN)',inplace=True)

	try:
		b = dfx.loc[ (dfx['REGICT']==0) & (dfx['PCT']>90) & (dfx['PCT']!=100) ].head(1)
		dfx.eval('MCP='+str(float(b.PCT)),inplace=True)
	except:
		dfx.eval('MCP=90',inplace=True)

	dfx.eval('gamma=(1-((PCT-MCP)/(100-MCP)))',inplace=True)
	#rectify gamma
	dfx.gamma[dfx.gamma>gamma_threshold]=gamma_threshold
	c = dfx.DIFF.mean()
	dfx.eval('C=abs('+str(float(c))+")",inplace=True)
	#INPULL FIN
	dfx.eval('FIN=REGFIN+C*gamma',inplace=True)
	dfx.eval('UFIN=FIN+C*gamma',inplace=True)
	dfx.eval('BFIN=FIN-C*gamma',inplace=True)
	print(dfx)
	return dfx
import os
import pandas as pd
import json
import matplotlib.pyplot as plt

def OutPut(filepath,enum,etp,df):
	"""this is a output configuation core, which the Graph and the Json is rendered here.
	>.IF YOU DONT KNOW WHAT YOURE DOING, DO NOT CHANGE ANY THING OF THIS.< 
	:enum ~ int * a number indecate the eventNumber
	:etp ~ int * a type indecate the eventType
	:filepath ~ str * a path to save things
	:df ~ DataFrame * which is the final DataFrame rendered by pandas 
	"""

	#saveAgement - Setting of General
	FILE_NAME = "e"+str(enum)+"t"+str(etp) 
	Jsonfilename = FILE_NAME+".json"
	ImgFilename = FILE_NAME+".png"

	#make Directory
	if not os.path.exists(filepath):
		os.mkdir(filepath)

	pred = df.plot.line(x='PCT', y='UFIN', color='black', label='U-Final Predict',marker='x')
	df.plot.line(x='PCT', y='REALY', color='blue', label='RealTime Value' ,marker='o', ax=pred, figsize=(10,10))
	plt.xlabel("pct,%")
	plt.ylabel("score")
	plt.xlim(0,105)
	plt.legend(loc="upper left")
	plt.grid(True)
	plt.savefig(filepath+"event_"+ImgFilename)
	print("GLOBAL PIC GENERATE -> ")

	if(len(df)>5):
		dfx = df[-5:]
		#first dataset
		pred = dfx.plot.scatter(x='PCT', y='FIN', color='green', label='Final Predict')
		pred = dfx.plot.scatter(x='PCT', y='UFIN', color='black', label='Upper Final Predict', ax=pred)
		pred = dfx.plot.scatter(x='PCT', y='BFIN', color='red', label='Bottom Final Predict', ax=pred)
		dfx.plot.line(x='PCT', y='REALY', color='blue', label='TrueValue', ax=pred, figsize=(10,10))
		plt.xlabel("pct,%")
		plt.ylabel("score")
		plt.legend(loc="upper left")
		plt.grid(True)
		plt.savefig(filepath+"event_zoomlast_"+ImgFilename)
		print("LAST PIC GENERATE -> ")

	dfp_json = df.to_json(orient = 'records', force_ascii = False)
	f = open(filepath+"event_json_"+Jsonfilename, 'w', encoding='utf-8')
	f.write(dfp_json)
	f.close()
	print("JSON GENERATE -> ")

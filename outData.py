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
	
	#make Directory
	if not os.path.exists(filepath):
		os.mkdir(filepath)

	dfp_json = df.to_json(orient = 'records', force_ascii = False)
	f = open(filepath+"event.json", 'w', encoding='utf-8')
	f.write(dfp_json)
	f.close()
	print("JSON GENERATE -> ")

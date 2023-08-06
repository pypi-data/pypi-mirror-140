#SHREYA GARG
#101953015

import pandas as pd
import numpy as np
import math
import copy
import sys
import os

def main():
	try:
		if(len(sys.argv)!=5):
			raise Exception("Please enter correct number of parameters.\nEnter in the format python <Filename> <InputDataFile> <Weights> <Impacts> <ResultCsvFilename>")
	except Exception as e:
		print(e)   
		exit(0)
	try:
	 	if not os.path.exists(sys.argv[1]) :
	 	   	raise Exception("No such {} file exists. Please enter a valid file name".format(sys.argv[1]))
	except Exception as e:
		print(e) 
		exit(0)
	try:
		if(sys.argv[1][-4:]=='.csv'):
			df=pd.read_csv(sys.argv[1])
		elif(sys.argv[1][-4:]=='.txt'):
			df=pd.read_csv(sys.argv[1],sep='\t')
		if len(df.columns)<3:
			raise Exception("Input file must contain three or more columns.")
	except Exception as e:
	    print(e)
	    exit(0)
	try:
		w=sys.argv[2]
		w=list(map(float,w.split(',')))
	except:
		print("The weights should be integer or float values and seperated by commas. For example:'1,1,1,2'")
		exit(0)
	try:
		imp=sys.argv[3]
		ti=list(filter(lambda k:k!=None,(map(lambda t:t if t!=',' else None ,imp ))))
		for i in ti:
			if(i!='+' and i!='-'):
				raise Exception("The impacts should be possitive(+) or negative(-) and seperated by commas. For example:'+,+,-,+'")
	except Exception as e:
		print(e)
		exit(0)			
	try:
		if(len(ti)!=(len(df.columns)-1) or len(w)!=(len(df.columns)-1) or len(ti)!=len(w)):
	 		raise Exception("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.")	
	except Exception as e:
	 	print(e)
	 	exit(0)
	try:
		for i in range(1,len(df.columns)):
			if(df[df.columns[i]].dtype!=np.int64 and df[df.columns[i]].dtype!=np.float64):
				raise Exception("From 2nd to last columns must contain numeric values only.")
	except Exception as e:
	 	print(e)
	 	exit(0)			 		
	x=pd.read_csv(sys.argv[1])
	mean_squares=[]
	for i in range(1,len(x.columns)):
	    t=[j*j for j in x.loc[0:,x.columns[i]]]
	    mean_squares.append(math.sqrt(sum(t)))
	normalized_decision_matrix=copy.copy(x)
	for i in range(1,len(x.columns)):
	    normalized_decision_matrix.loc[0:,x.columns[i]]=normalized_decision_matrix.loc[0:,x.columns[i]]/mean_squares[i-1]
	weightage=str(sys.argv[2])
	weightage=list(map(float,weightage.split(',')))
	weighted_normalized_decision_matrix=copy.copy(normalized_decision_matrix)
	for i in range(1,len(x.columns)):
	    weighted_normalized_decision_matrix.loc[0:,x.columns[i]]=weighted_normalized_decision_matrix.loc[0:,x.columns[i]]*weightage[i-1] 
	Impacts=list(sys.argv[3])
	Impacts=list(filter(lambda k:k!=None,(map(lambda t:t if t!=',' else None ,Impacts ))))
	Vplus=[]
	Vminus=[]
	for i in range(1,len(x.columns)):
	    if(Impacts[i-1]=='+'):
	        Vplus.append(max(weighted_normalized_decision_matrix.loc[0:,x.columns[i]]))
	        Vminus.append(min(weighted_normalized_decision_matrix.loc[0:,x.columns[i]]))
	    else:
	        Vplus.append(min(weighted_normalized_decision_matrix.loc[0:,x.columns[i]]))
	        Vminus.append(max(weighted_normalized_decision_matrix.loc[0:,x.columns[i]]))     
	l=[]
	t=[]
	pplus=pd.Series(dtype='float64')
	mminus=pd.Series(dtype='float64')
	for i in range(len(x.index)):
	    for j in range(1,len(x.columns)):
	        l.append((weighted_normalized_decision_matrix.loc[i][j]-Vplus[j-1])**2)
	        t.append((weighted_normalized_decision_matrix.loc[i][j]-Vminus[j-1])**2)
	    pplus.at[i]= math.sqrt(sum(l))
	    mminus.at[i]=math.sqrt(sum(t))
	    l=[]
	    t=[]
	weighted_normalized_decision_matrix['pplus']=pplus
	weighted_normalized_decision_matrix['mminus']=mminus
	weighted_normalized_decision_matrix['pplus+mminus']=weighted_normalized_decision_matrix.pplus+weighted_normalized_decision_matrix.mminus
	weighted_normalized_decision_matrix['Topsis Score']=weighted_normalized_decision_matrix.mminus/weighted_normalized_decision_matrix['pplus+mminus']
	weighted_normalized_decision_matrix['Rank']=weighted_normalized_decision_matrix['Topsis Score'].rank(ascending=0)
	x['Topsis Score']=weighted_normalized_decision_matrix['Topsis Score']
	x['Rank']=weighted_normalized_decision_matrix['Rank']
	x.to_csv(sys.argv[4])
#     print("Done")

if __name__=="__main__":
	main()	
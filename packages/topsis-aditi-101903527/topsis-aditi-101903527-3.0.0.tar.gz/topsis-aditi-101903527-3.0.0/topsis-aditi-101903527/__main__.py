def main():
	# -*- coding: utf-8 -*-
	"""
	Created by:
	    ADITI
	    101903527
	    2CO20
	"""

	import numpy as np
	import pandas as pd
	from datetime import datetime,timezone
	import os
	import sys
	import pytz

	os.chdir('E:/6th sem/predictive_analysis/assignments/ass4') #change working directory to read files from this directroy

	log=open('logg.txt','w+')
	log.close()
	log=open('logg.txt','a')
	file_name=sys.argv[1]
	weight=sys.argv[2]
	impact=sys.argv[3]
	res_name=sys.argv[4]
	print(len(sys.argv))


	#checking for correct number of arguments
	if len(sys.argv)==5:
	    check=isinstance(file_name,str) and isinstance(weight,str) and isinstance(impact,str) and isinstance(res_name,str)
	    if check==False:
	        dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	        log.write('Datetime: %s , Exception : Check input parameters entered\n'%(dt))
	else:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Wrong number of input parameters entered\n'%(dt))
	    raise SystemExit
	    
	   
	weigh=weight.split(',')
	imp=impact.split(',')


	#check for correct input file format
	if file_name.endswith('xlsx'):                          #showing exception for wrong file format
	  pass
	else:
	  dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	  log.write('Datetime: %s , Exception : Input parameter not correct. Non xlsx file entered\n'%(dt))
	  raise Exception('Wrong input file format')

	 

	#reading in the input file 
	try:
	  df=pd.read_excel(file_name)
	except FileNotFoundError:                              #showing exception when file not found
	  dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	  log.write('Datetime: %s , Exception : Input file not found\n'%(dt))
	  raise SystemExit


	#converting 
	try:
	    df.to_csv('input.csv',index=None,header=True)
	except:
	   dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	   log.write('Datetime: %s , Exception : File conversion from xlsx to csv failed\n'%(dt))
	   raise SystemExit 
	   


	#checking for correctness of other input parameters
	ncols=len(df.columns)
	if len(weigh)==ncols-1:
	    pass
	else:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Check weights entered. Wrong number of weights entered\n'%(dt))
	    raise SystemExit
	    
	if all(w.isdigit() for w in weigh)==False:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Check weights entered. Non numeric weights entered\n'%(dt))
	    raise SystemExit
	    
	if len(imp)==ncols-1:
	    pass
	else:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Check impacts entered. Wrong number of impacts entered\n'%(dt))
	    raise SystemExit
	    
	check=True
	for i in range(len(imp)):
	    if (imp[i]!="+") and (imp[i]!="-"):
	        check=False
	        break

	if check==False:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Check impacts entered. Non valid impact entered\n'%(dt))
	    raise SystemExit


	#checking for correct number of columns
	if ncols>=3:
	    pass
	else:
	    dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	    log.write('Datetime: %s , Exception : Number of columns in input file not equal to 3\n'%(dt))
	    raise Exception('Less number of columns in input file')
	    
	#checking for correct number of numeric columns
	for i in range(len(df.columns)):
	    if i<1:
	        continue
	    val=(pd.to_numeric(df[df.columns[i]],errors='coerce').notnull().all())
	    if val==False:
	        dt=datetime.now(pytz.timezone('Asia/Kolkata'))
	        log.write('Datetime: %s , Exception : Non numeric columns\n'%(dt))
	        raise SystemExit
	   
	print(df.head())

	wt=[]
	for i in range(len(weigh)):
	    wt.append(float(weigh[i]))
	    
	    
	#step 1 : calculate root of sum of squares of every column
	s=[]
	cols =[]
	for i in range(len(df.columns)):
	    if i==0:
	        continue
	    cols.append(df.columns[i])

	for c in cols:
	  sum=0
	  for x in df[c]:
	    sum+=(x**2)
	  sum=(sum ** (1/2))
	  s.append(sum)


	#step 2: normalize all column values using the found root of sum of sqs
	for j in range(1,5):
	  for i in range(0,len(df.iloc[:,0])):
	    df.iloc[i,j]=df.iloc[i,j]/s[j-1]


	#step 3: assigning weight to every column
	i=0
	for c in cols:
	  df[c]=np.array(df[c])*wt[i]
	  i+=1


	#find ideal best and ideal worst
	ib=[]
	iw=[]
	i=0
	for c in cols:
	  mx=np.array(df[c]).max()
	  mn=np.array(df[c]).min()
	  if imp[i]=='+':
	    ib.append(mx)
	    iw.append(mn)
	  else:
	    ib.append(mn)
	    iw.append(mx)
	  i+=1
	  

	#finding euclidean distance of each row from ideal best and ideal worst
	edib=[]       
	ediw=[]
	for i in range(0,len(df)):
	  edib.append((np.sum((np.array(df.iloc[i,1:])-np.array(ib))**2))**(1/2))
	  ediw.append((np.sum((np.array(df.iloc[i,1:])-np.array(iw))**2))**(1/2))



	performance=list(np.array(ediw)/((np.array(ediw)+np.array(edib))))

	rank=np.array([1]*len(performance))

	for i in range(0,len(performance)):
	  for j in range(0,len(performance)):
	    if i==j:
	      continue
	    if performance[j]>=performance[i]:
	      rank[i]+=1

	dfout=df
	dfout['Topsis Score']=performance
	dfout['Rank']=rank
	print(dfout)

	dfout.to_csv(res_name)


if __name__ =='__main__':
	main()
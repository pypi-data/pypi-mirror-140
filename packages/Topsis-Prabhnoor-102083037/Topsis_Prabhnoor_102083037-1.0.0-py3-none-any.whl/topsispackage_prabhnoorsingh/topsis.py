import pandas as pd
import numpy as np


def norm_dataframe(data):
  normalized = pd.DataFrame()
  data.iloc[:,1:].astype(float,errors='raise')
  for i in range(1,len(data.columns)):
    normalized = pd.concat([normalized,data.iloc[:,i]/np.linalg.norm(data.iloc[:,i])],axis=1)
  return normalized


def topsis_calc(data,weights,impacts):
    
  if len(data.columns)-1==len(weights)==len(impacts):
    pass
  else:
    raise Exception("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.")
 
  nor = norm_dataframe(data)
  for x in weights:
    if not isinstance(x,(float,int)):
      raise Exception("Weights must be numeric")
  w_nor = nor*weights
  no_feature = len(w_nor.columns)
  j = 0
  best = []
  worst = []
  
  for i in impacts:
    if i=='+':
      best.append(max(w_nor.iloc[:,j]))
      worst.append(min(w_nor.iloc[:,j]))
    elif i=='-':
      worst.append(max(w_nor.iloc[:,j]))
      best.append(min(w_nor.iloc[:,j]))
    else:
      raise Exception("Impact only takes + and - as its values")       
    j = j+1

  w_nor['s+'] = 0
  w_nor['s-'] = 0

  for i in range(0,len(w_nor.index)):
    w_nor.iloc[i,no_feature] = sum((w_nor.iloc[i,0:no_feature]-best)**2)**0.5
    w_nor.iloc[i,no_feature+1] = sum((w_nor.iloc[i,0:no_feature]-worst)**2)**0.5

  w_nor['Topsis Score'] = 0
  
  for i in range(0,len(w_nor.index)):
    w_nor.loc[i,'Topsis Score'] = w_nor.loc[i,'s-']/(w_nor.loc[i,'s+']+w_nor.loc[i,'s-'])

  w_nor['Rank'] = w_nor['Topsis Score'].rank(ascending=False)
  final = pd.concat([data,w_nor[['Topsis Score', 'Rank']]],axis=1)
  return final


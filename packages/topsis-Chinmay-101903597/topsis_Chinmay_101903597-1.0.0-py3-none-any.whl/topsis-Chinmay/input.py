# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 23:26:54 2022

@author: DELL
"""

import sys
import math
import pandas as pd
import numpy as np

def euclidean(r,c,data,maxData,minData,euclidPlus,euclidMinus):
    for i in range(r):
      sum = 0
      for j in range(c):
         sum += pow((data[i][j] - maxData[j]), 2)
      euclidPlus.append(float(pow(sum, 0.5)))

    for i in range(r):
      sum = 0
      for j in range(c):
         sum += pow((data[i][j] - minData[j]), 2)
      euclidMinus.append(float(pow(sum, 0.5)))
      
    return euclidPlus,euclidMinus      
      
def calc(r,c,data,weights,rms,totalW):
   for i in range(0,r):
      for j in range(0,c):
         rms[j] += (data[i][j] * data[i][j])

   for j in range(c):
      rms[j] = math.sqrt(rms[j])        
         
   for i in range(c):
      weights[i] /= totalW

   for i in range(r):
      for j in range(c):
         data[i][j] = (data[i][j] / rms[j]) * weights[j]
         
   return data
   
def main():
   if len(sys.argv) != 5:
      print('Incorrect number of parameters')
      exit(0)

   try:
      w = list(map(float, sys.argv[2].split(',')))
      impact = list(map(str, sys.argv[3].split(','))) 
   except:
      print('Separate weights and impacts with commas')
      exit(0)
         
   for ch in impact:
      if ch not in ('+','-'):
         print('Incorrect impacts')
         exit(0)

   result = sys.argv[4]

   try:
      df = pd.read_csv(sys.argv[1])
   except:
      print('File not found')
      exit(0)
         
   if len(list(df.columns)) < 3:
      print('Less than 3 columns not allowed')
      exit(0)
         
   data=df
   df.drop(['Fund Name'],inplace=True, axis = 1)
   (r,c) = df.shape
   
   if len(w) !=c or len(impact) != c:
      print("Incorrect number of weights or impacts")
      exit(0)
      
   df = df.values.astype(float)
   totalW = np.sum(w)
   rms = [0]*(data.shape[1])
   
   df=calc(df.shape[0],df.shape[1],df,w,rms,totalW)
   maximumData = np.amax(df, axis = 0) 
   minimumData = np.amin(df, axis = 0)
   
   for i in range(len(impact)):
      if(impact[i] == '-'):         
         temp = maximumData[i]
         maximumData[i] = minimumData[i]
         minimumData[i] = temp

   euclideanPlus = []
   euclideanMinus = []
   
   euclideanPlus,euclideanMinus=euclidean(df.shape[0], df.shape[1], df, maximumData, minimumData, euclideanPlus, euclideanMinus)
   
   performance = {}

   for i in range(df.shape[0]):
      performance[i + 1] = euclideanMinus[i] / (euclideanMinus[i] + euclideanPlus[i])

   p = list(performance.values())
   performanceFinal = sorted(list(performance.values()), reverse = True)

   rank = {}

   for val in p:
      rank[(performanceFinal.index(val) + 1)] = val
      
   

   output = data
   output['Topsis Score'] = list(rank.values())
   output['Rank'] = list(rank.keys())

   res = pd.DataFrame(output)
   res.to_csv(result, index = False)
   

if __name__ == "__main__":
   main()
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   

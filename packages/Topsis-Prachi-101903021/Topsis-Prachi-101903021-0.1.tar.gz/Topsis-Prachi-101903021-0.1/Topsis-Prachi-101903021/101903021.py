# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 01:06:37 2022

@author: Asus
"""
import pandas as pd
import  numpy as np
import sys
import math as m

# from collections import defaultdict
def logging():
    if len(sys.argv)!=5 :
        raise Exception("please enter four parameters")
    if sys.argv[1].endswith(('.csv')):
        pass
    else:
        raise Exception("file not a csv type")

    filename=sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    outputFile=sys.argv[4]
    
#split() cuts provided input on whitespaces into a list.
#name, *line assigns first item to name, and the rest lands in the list line

#list(map(float, line)) creates a derivative list where each item from line is mapped/converted to float. Equivalent to scores = [float(x) for x in line]
    weights = list(map(float ,weights.split(',')))
    impacts = list(map(str ,impacts.split(',')))

    for imp in  impacts:
        if imp =='+' or imp=='-':
            pass
        
        else:
            raise Exception("impact must be positive(+) or negative (-)")
    try:
        dataset,temp_dataset = pd.read_csv(filename),pd.read_csv(filename)
    except:
        print("File Not Found")
        sys.exit()
    print(dataset)
    data=[]
    try:
        data=dataset.iloc[ :,1:].values.astype(float)
    except ValueError:
        print("Not all data in CSV file is numeric")
        sys.exit()
    data=dataset.iloc[ :,1:].values.astype(float)
    (r,c)=data.shape

    if c<3:
        raise Exception("Insufficient data in CSV file(less than 3 columns)")
    

    if len(weights) != c:
        raise Exception("Weights data not matched with input file")
    if len(impacts) != c:
        raise Exception("Impacts data not matched with input file")
    topsis_cal(temp_dataset,dataset,c,weights,impacts)
    dataset.to_csv(outputFile,index=False)
    
    
def topsis_cal(temp_dataset,dataset,c,weights,impacts):
  
    #step1: normalisation and weigght assignment
  for i in range(1, c):
        temp = 0
        for j in range(len(temp_dataset)):
            temp = temp + temp_dataset.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(temp_dataset)):
            temp_dataset.iat[j, i] = (temp_dataset.iloc[j, i] / temp)*weights[i-1]
  
    #step2: ideal best and worst acc to impacts
  max_val=(temp_dataset.max().values)[1:]
  min_val=(temp_dataset.min().values)[1:]
  for i in range(1, c):
            if impacts[i-1] == '-':
                max_val[i-1], min_val[i-1] = min_val[i-1], max_val[i-1]
    
    #step3:Calculate Euclidean distance from ideal best value and ideal worst value
  score=[]
  for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, c):
            temp_p = temp_p + (max_val[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (min_val[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
  dataset['Topsis Score'] = score
  dataset['Rank'] = (dataset['Topsis Score'].rank(
  method='max', ascending=False))
  dataset = dataset.astype({"Rank": int})
  dataset.to_csv(sys.argv[4], index=False)
            


if __name__ == "__main__":
    logging()
        
            
 
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 12:10:28 2022

@author: chavvi
"""

import pandas as pd
import numpy as np
import sys
import os.path
from pandas.api.types import is_numeric_dtype


def normalize(d,w):
    for i in range(d.shape[1]):
        sum=0
        for j in list(d.iloc[:,i]):
                sum+=j**2
        den=sum**0.5
        for ind,k in enumerate(list(d.iloc[:,i])):
            d.iloc[ind,i]=k*float(w[i])/den
            
def ideal(df,impact):
    idealbest=[]
    idealworst=[]
    for i in range(df.shape[1]):
        if impact[i]==1:
            idealbest.append(df.max()[i])
            idealworst.append(df.min()[i])
        else:
            idealbest.append(df.min()[i])
            idealworst.append(df.max()[i])
            
    return idealbest,idealworst

def cal_score(d,idealbest,idealworst):
    distance_positive=[]
    distance_negative=[]
    score=[]
    for i in range(d.shape[0]):
        distance_positive.append(np.linalg.norm(d.iloc[i,:]-idealbest))
        distance_negative.append(np.linalg.norm(d.iloc[i,:]-idealworst))
        
    for i in range(len(distance_positive)):
        score.append(distance_negative[i]/(distance_negative[i]+distance_positive[i]))
    return score

def topsis(data,weight,impact,output):
    i=pd.read_csv(data)
    ##########
    try:
        if not os.path.exists(data):
            raise Exception("INPUT FILE DOES NOT EXIST")
    except Exception as e:
        print(e)
        exit(0)
        #exit(0)
    ##########
    
    ##########
    try:
        if len(sys.argv)!=5:
            raise Exception("5 ARGUMENTS NEEDED!")
    except Exception as e:
        print(e)
        exit(0) 
        #exit(0)
    ##########
    
    ##########
    try:
        if len(i.columns)<3:
            raise Exception("INPUT FILE MUST CONATIN 3 OR MORE COLUMNS")
    except Exception as e:
        print(e)
        exit(0)
        #exit(0)
    ##########
    for j in range(1,len(i.columns)):
        if(is_numeric_dtype(i.iloc[:,j])==False):
            print(i+"th COLUMN MUST CONATIN NUMERIC VALUES ONLY")
    ##########
    try:
        #weight = sys.argv[2]
        weight = list(map(float, weight.split(',')))
    except:
        print("The weights should be sepearted by commas")
        exit(0)
        #exit(0)
        
    try:
        impact = impact.split(',')
        
    except:
        print("The impacts should be sepearted by commas")
        exit(0)
        #exit(0)
        
    ##########
    try:
        for j in range(len(impact)):
            if impact[j]=="+" or impact[j]=="-":
                continue
            else:
                raise Exception("IMPACTS MUST BE EITHER +VE OR -VE")
                #exit(0)
    except Exception as e:
        print(e)
        exit(0)
        
    impact = list(map(lambda x:x.replace('+','1'),impact))
    impact = list(map(lambda x:x.replace('-','-1'),impact))
    impact = [int(i) for i in impact]
    
    try:
        if((len(weight)==len(impact) and len(weight)==len(i.columns)-1)==False):
            raise Exception("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same")
        #exit(0)
    except Exception as e:
        print(e)
        exit(0)
 
    d=i.iloc[:,1:]
    normalize(d,weight)
    idealbest,idealworst=ideal(d,impact)
    top=cal_score(d, idealbest, idealworst)
    table=i
    table['Topsis Score'] = top
    j = 1
    t = top
    t = list(t)
    rank={}
    while len(t)!=0:
        rank[max(t)] = j
        t.remove(max(t))
        j = j + 1
        
    table['Rank'] = table["Topsis Score"].map(rank)
    table.to_csv(output,index=False)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 08:34:47 2020

@author: sharma._.g
"""

import pandas as pd
import sys as sys
import math as math
import operator

def main():
    if(len(sys.argv)!=4):
        print("Number of input arguments are not correct!!! ")
        exit(0)
    
    dataset=pd.read_csv(sys.argv[1])
    weights=[float(w) for w in sys.argv[2].split(',')]
    impacts=[i for i in sys.argv[3].split(',')]
    
    if(len(weights)!=dataset.shape[1]-1):
        print("Number of weights are not correct!!!")
        exit(0)
        
    if(len(impacts)!=dataset.shape[1]-1):
        print("Number of impacts are not correct!!!")
        exit(0)
        
    dataset2=dataset.iloc[:,1:].values
    try:
        weights=[w/sum(weights) for w in weights ]
    except:
        print("Exception 1 raised! Check the code and inputs again.")
        
    for i in range(dataset2.shape[1]):
        n=math.sqrt(sum(dataset2[:,i]**2))
        for j in range(dataset2.shape[0]):
            try:
                dataset2[j][i]=dataset2[j][i]/n
            except:
                print("Exception 2 raised! Check the code and inputs again.")
        
    for i in range(len(weights)):
        dataset2[:,i]=dataset2[:,i]*weights[i]
        
    best=[]
    worst=[]
    for i in range(len(impacts)):
        if(impacts[i]=='+'):
            best.append(max(dataset2[:,i]))
            worst.append(min(dataset2[:,i]))
        else:
            best.append(min(dataset2[:,i]))
            worst.append(max(dataset2[:,i]))
        
    dbest=[]
    dworst=[]
    for i in range(dataset2.shape[0]):
        sum1=0
        sum2=0
        for j in range(dataset2.shape[1]):
            sum1=sum1+(dataset2[i,j]-best[j])**2
            sum1=math.sqrt(sum1)
            sum2=sum2+(dataset2[i,j]-worst[j])**2
            sum2=math.sqrt(sum2)
        dbest.append(sum1)
        dworst.append(sum2)
        
    per=[]
    for i in range(len(dbest)):
        try:
            per.append(dworst[i]/(dworst[i]+dbest[i]))
        except:
            print("Exception 3 raised! Check the code and inputs again.")
           
    matrix=[]
    for i in range(len(per)):
        matrix.append([i+1,dataset.iloc[i,0],per[i],0])
        
    matrix.sort(key=operator.itemgetter(2))
        
    for i in range(len(matrix)):
        matrix[i][3]=len(matrix)-i
        
    matrix.sort(key=operator.itemgetter(0))
        
    for i in range(len(matrix)):
        print(matrix[i][1]+" ranks "+str(matrix[i][3]))

if __name__=="__main__":
    main()
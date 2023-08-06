import sys
import csv
import pandas as pd
import os
import copy
import math
import numpy as np
from os import path

def main():
    class  myexception(Exception):
        pass
    filename = sys.argv[1]
    # print(filename)
    # f = open(filename,'r')
    if not (path.exists(filename)):
        raise myexception("No such file exists")
    if not filename.endswith('.csv'):
        raise myexception("Enter CSV format file only")
    dataset = pd.read_csv(filename)
    col = dataset.shape
    if not col[1]>=3:
        raise myexception("Input file must contain 3 or more columns")
    k=0
    for i in dataset.columns:
        k=k+1
        for j in dataset.index:
            if k!=1:
                val=isinstance(dataset[i][j],int)
                val1=isinstance(dataset[i][j],float)
                if not val and not val1:
                    raise myexception("Values are not numeric")
    # print(dataset)
    weights = sys.argv[2]
    we=weights.split(',')
    weights = list(map(int, we))
            # w.append(float(i))


    impact = []
    im = list(sys.argv[3])
    for i in im:
        if(i!=','):
            impact.append((i))

    if len(weights)!=(col[1]-1):
        raise myexception("Number of weight and number of columns must be equal")
    for i in impact:
        if i not in {'+','-'}:
            raise myexception("Format of impact is not correct")
        if len(impact)!=col[1]-1:
            raise myexception("Number of impact and Number of columns must be equal")
    temp_dataset = dataset
    nCol = 6
    def Normalize(dataset, nCol, weights):
        for i in range(1, nCol):
            temp = 0
            for j in range(len(dataset)):
                temp = temp + dataset.iloc[j, i]**2
            temp = temp**0.5
            for j in range(len(dataset)):
                dataset.iat[j, i] = (dataset.iloc[j, i] / temp)*weights[i-1]
        # print(dataset)
    # print(type(dataset.iloc[1,1]))


    # print(weights)



    # print(impact)

    Normalize(dataset,nCol,weights)
    def Calc_Values(dataset, nCol, impact):
        p_sln = (dataset.max().values)[1:]
        n_sln = (dataset.min().values)[1:]
        for i in range(1, nCol):
            if impact[i-1] == '-':
                p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
        return p_sln, n_sln

    p_sln, n_sln = Calc_Values(temp_dataset, nCol, impact)
    score = [] 
    
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, nCol):
            temp_p = temp_p + (p_sln[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))

    dataset['Topsis Score'] = score
    

    dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})
    # print(dataset)
    dataset.to_csv(sys.argv[4],index = False)



import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import re
from scipy.stats import rankdata
from argparse import ArgumentParser
from collections import Counter

def main():    
    if len(sys.argv) >= 4:
        file = sys.argv[1]
        weights = list(map(float, sys.argv[2].strip().split(',')))
        impacts = list(sys.argv[3].strip().split(','))
        assert "csv" in f"{file}", "Could not recognize csv file, try checking your input file"
        data = pd.read_csv(file).iloc[:, 1:]
        if len(sys.argv) == 5:
            opfile = sys.argv[4]
            calc(data , weights , impacts, opfile)
        else:
            opfile = "101903150-result"
            calc(data , weights , impacts, opfile)
    else:
        print("PUT ARGUMENTS IN ORDER : python -m topsis.topsis <InputDataFile> <Weights> <Impacts> <ResultFileName>")
    print(data)
    
    
    
def calc(data , weights , impacts, opfile):
    n,m=data.shape
    df=data.iloc[:,1:]
    x=df.values.tolist()
    for j in range(0,len(x[0])):
        sumsq=0
        for i in range(0,n):
            sumsq+=x[i][j]**2
        sumsq=sumsq**0.5
        for i in range(0,len(x)):
            x[i][j]/=sumsq   
    #print(x)
    
    weight = list(weights)      
    # for i in range(1,len(x)):
    #     for j in range(1,len(x[0])):
    #         x[i][j]*=weight[i]
    mat = np.array(x, dtype = np.float64)
    col = len(mat[0])
    row = len(mat)
    # n_mat = np.array([[0]*col for _ in range(row)], dtype = np.float64)
    # for i in range(col):
    #     temp = np.sum(mat[:, i]**2)**0.5
    #     n_mat[:, i] = mat[:, i] / temp
    w_mat = np.array([[0]*col for _ in range(row)], dtype = np.float64)
    for i in range(col):
            w_mat[:, i] = mat[:, i] * weights[i]
    best = np.array([0]*col, dtype = np.float64)
    worst = np.array([0]*col, dtype = np.float64)
    mat=w_mat
    for i in range(col):
        best[i] = np.max(mat[:, i])
        worst[i] = np.min(mat[:, i])
        if impacts[i] == "-":
            best[i],worst[i] = worst[i],best[i]    

    from_best = np.array([0]*row, dtype = np.float64)
    from_worst = np.array([0]*row, dtype = np.float64)
    pfm = np.array([0]*row, dtype = np.float64)
    ranks = np.array([0]*row, dtype = np.float64)
    for i in range(row):
        from_best[i] = np.sum((mat[i, :] - best)**2)**0.5
        from_worst[i] = np.sum((mat[i, :] - worst)**2)**0.5
        pfm = from_worst/(from_best + from_worst)
    pfm = pfm.tolist()
    ranks = len(pfm)-rankdata(pfm).astype(int)+1

    data['Topsis Score']=pfm
    data['Rank']=ranks
    data.to_csv(f'{opfile}',index=False')
        

if __name__ == "__main__":
    main()
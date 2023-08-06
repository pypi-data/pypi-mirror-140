# DIVYANSH KAUSHIK
# 102083048
# 3CO2

import os
import sys
import numpy as np
import pandas as pd

def topsis(decision,weights,impacts,output):
    df = pd.read_csv(decision, header=None)  # reading input csv file
    assert df.shape[1] > 3, "Input File must contain three or more columns"
    nameCOl = df.iloc[:,0]    
    nameRow = df.iloc[0,:]
    decision = df.iloc[1:,1:]
    weights = weights.strip('"').split(',')
    impacts = impacts.strip('"').split(',')
    assert len(impacts) == len(weights), "Mismatch between length of impacts and weights"
    assert len(weights) == df.shape[1]-1, "Mismatch between length of weights and number of columns of input data"

    decision = np.array(decision).astype(float) # .astype(float) method sets or converts the data type of an existing data column in a dataset or a data frame to float data type
    weights = np.array(weights).astype(float)
    impacts = [char for char in impacts]
    
    nrow = decision.shape[0]  # finding number of rows in given input file using shape funcion
    ncol = decision.shape[1]  # finding number of columns in given input file using shape function
    
    # Program will raise appropriate error if these conditions are not met
    assert len(decision.shape) == 2, "Decision matrix must be two dimensional"
    assert len(weights.shape) == 1, "Weights array must be one dimensional"
    assert len(weights) == ncol, "Wrong length of Weights array, should be {}".format(ncol)
    assert len(impacts) == ncol,"Wrong length of Impacts array, should be {}".format(ncol)
    
    # scaling weights
    weights = weights/sum(weights)
    
    # initializing N 
    N = np.zeros((nrow,ncol))
    
    nf = [None]*ncol
    for j in range(ncol):
        nf[j] = np.sqrt(sum((decision[:,j])**2))
    
    # constructing normalized decision matrix
    for i in range(nrow):
        for j in range(ncol):
            N[i][j] = decision[i][j]/nf[j]
    
    # constructing weighted normalized decision matrix
    W = np.diag(weights)
    V = np.matmul(N,W)
    
    # determination of ideal best and ideal worst solutions
    u = [max(V[:,j]) if impacts[j] == '+' else min(V[:,j]) for j in range(ncol)]
    l = [max(V[:,j]) if impacts[j] == '-' else min(V[:,j]) for j in range(ncol) ]
    
    # calculating Euclidean distance from ideal best value and ideal worst value
    du = [None]*nrow
    dl = [None]*nrow
    
    
    for i in range(nrow):
        du[i] = np.sqrt(sum([(_v - _u)**2 for _v,_u in zip(V[i],u) ]))
    for i in range(nrow):
        dl[i] = np.sqrt(sum([(_v - _l)**2 for _v,_l in zip(V[i],l) ]))
    
    du = np.array(du).astype(float)
    dl = np.array(dl).astype(float)
    
    # calculatingg relative closeness to ideal solution or Calculating Performance Score
    score = dl/(dl+du)
    
    # This part is to return a dataframe with results - alternatives with their corresponding score and rank
    index = pd.Series([i+1 for i in range(nrow)])
    score = pd.Series(score)
    ranks = score.rank(ascending = False,method = 'min').astype(int)
    result = pd.concat([index,score, ranks], axis=1)
    result.columns = ['Alternative','Topsis Score','Rank']
    result = result.set_index('Alternative')
    result.loc[0] = ['Topsis Score','Rank']
    result = pd.concat([df,result], axis = 1)
    result.to_csv(output, header = False, index=False)


def Output():
    if len(sys.argv) != 5:
        print('Insufficient number of arguments')
        print('Input should be like - python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>')
    else:
        file_path = sys.argv[1]
        try:                               #Handling "File Not Found" exception
            if os.path.exists(file_path):
                print('Input File exist')
        except OSError as err:
            print(err.reason)
            exit(1)

        outputfile = sys.argv[4]
        assert '.csv' in outputfile, "output File extension must be ,csv"
        assert '.csv' in file_path, "input File extension must be .csv"

        topsis(file_path, sys.argv[2], sys.argv[3],outputfile)
        


if __name__ == '__main__':
    Output()
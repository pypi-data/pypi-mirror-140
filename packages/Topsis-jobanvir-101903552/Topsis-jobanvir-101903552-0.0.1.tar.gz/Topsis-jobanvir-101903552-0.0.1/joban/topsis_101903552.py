import numpy as np
import pandas as pd
import sys

def topsis(decision,weights,impacts):
    decision = np.array(decision).astype(float)
    weights = np.array(weights).astype(float)
    impacts = [char for char in impacts]
    
    nrow = decision.shape[0]
    ncol = decision.shape[1]
    
    # Program will raise appropriate error if these conditions are not met
    assert len(decision.shape) == 2, "Decision matrix must be two dimensional"
    assert len(weights.shape) == 1, "Weights array must be one dimensional"
    assert len(weights) == ncol, "Wrong length of Weights array, should be {}".format(ncol)
    assert len(impacts) == ncol,"Wrong length of Impacts array, should be {}".format(ncol)
    assert len(weights) == ncol and len(impacts) == ncol, "Parameter are not of same length"
    assert [(impacts[i] == '+' or impacts[i] == '-') for i in range(ncol)], "Other than + or -"

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
            decision[i][j] = N[i][j]
    
    # constructing weighted normalized matrix
    W = np.diag(weights)
    V = np.matmul(N,W)
    
    # determination of positive ideal and negative ideal solutions
    u = [max(V[:,j]) if impacts[j] == '+' else min(V[:,j]) for j in range(ncol)]
    l = [max(V[:,j]) if impacts[j] == '-' else min(V[:,j]) for j in range(ncol) ]
    
    # calculating separation measures - distance from best and distance from worst 
    du = [None]*nrow
    dl = [None]*nrow
    
    
    for i in range(nrow):
        du[i] = np.sqrt(sum([(_v - _u)**2 for _v,_u in zip(V[i],u) ]))
    for i in range(nrow):
        dl[i] = np.sqrt(sum([(_v - _l)**2 for _v,_l in zip(V[i],l) ]))
    
    du = np.array(du).astype(float)
    dl = np.array(dl).astype(float)
    
    # calculatingg relative closeness to ideal solution
    score = dl/(dl+du)
    
    # This part is to return a dataframe with results - alternatives with their corresponding score and rank
    fd = pd.DataFrame(V)
    index = pd.Series([i+1 for i in range(nrow)])
    score = pd.Series(score)
    ranks = score.rank(ascending = False,method = 'min').astype(int)
    result = pd.concat([fd,score, ranks], axis=1)
    # result.columns = ['Alternative','Score','Rank']
    # result = result.set_index('Alternative')
    return result





#####################
#####################
#####################


def main():
    arguments = sys.argv[1:]
    assert len(arguments) == 4, "Insufficient number of arguments provided, 4 required"

    filename = sys.argv[1]
    assert filename, "Filename must be provided"
    assert '.csv' in filename, "File extension must be .csv"    

    try:
        with open(filename) as f:
            print("File present")
    except FileNotFoundError:
        print('File is not present')


    dataframe = pd.read_csv(filename,header=0)
    assert dataframe.shape[1] >= 3, "File must contain 3 or more columns"
    assert (dataframe.iloc[:,1:].select_dtypes(exclude=["float", 'int'])).empty, "Non-numeric data"

    name = dataframe.iloc[:,0]
    data = dataframe.iloc[:,1:]
    colnames = dataframe.columns
    weights = sys.argv[2].split(',')
    impacts = sys.argv[3].split(',')
    assert len(impacts) == len(weights), "Mismatch between length of impacts and weights"

    output = topsis(data,weights,impacts)
    ranks = output.iloc[:,-1]
    max_index = ranks.idxmin()

    # print("\n|| The best alternative is {} ||\n".format(name[max_index-1]))
    print("The breakdown of scores and ranks is:\n=====================================================================================\n")

    colnames = colnames.append(pd.Index(['Topsis Score','Rank']))
    output = pd.concat([name,output], axis = 1)
    output.columns = colnames

    # print(output)
    output.to_csv('101917169-result.csv', index=False)
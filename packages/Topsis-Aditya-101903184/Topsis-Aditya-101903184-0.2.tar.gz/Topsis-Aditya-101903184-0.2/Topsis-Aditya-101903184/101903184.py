
import numpy as np 
import pandas as pd
import copy
import sys

def main():

    try:
        args = sys.argv
        inputFile = args[1]
        weights = args[2]
        impact = args[3]
        resultFile = args[4]
    except IndexError:
        print("NOT ENOUGH ARGUMENTS")
        return
    run(sys.argv) 

def Normalize(dataset, nCol, weights):
    for i in range(1, nCol):
        temp = 0
        
        for j in range(len(dataset)):
            temp = temp + dataset.iloc[j, i]**2
        temp = temp**0.5
        
        for j in range(len(dataset)):
            dataset.iat[j, i] = (dataset.iloc[j, i] / temp)*weights[i-1]

    
def Calc_Values(dataset, nCol, impact):
    p_sln = (dataset.max().values)[1:]
    n_sln = (dataset.min().values)[1:]
    for i in range(1, nCol):
        if impact[i-1] == '-':
            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
    return p_sln, n_sln


def doRanking(temp_dataset,nCol,impact,dataset):
    p_sln, n_sln = Calc_Values(temp_dataset, nCol, impact)

    
    score = [] # Topsis score
    pp = [] # distance positive
    nn = [] # distance negative

    
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, nCol):
            temp_p = temp_p + (p_sln[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
        nn.append(temp_n)
        pp.append(temp_p)

    
    dataset['Topsis Score'] = score

    # calculating the rank according to topsis score
    dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})

def run(args):
    inputFile = args[1]
    weights = list(map(int,args[2].split(',')))
    impact = list(args[3].split(','))
    resultFile = args[4]
    
    data = None
    try:
        data = pd.read_csv(inputFile)
    except:
        print("FILE NOT FOUND")
        return 
    n = len(data.columns)
    if not n > 3:
        print("Input File does not contain enough columns")
        return 
    
    temp_data = copy.deepcopy(data)

    Normalize(temp_data,n,weights)

    doRanking(temp_data,n,impact,data)

    #Writing it out 
    data.to_csv(resultFile,index=False)

main()
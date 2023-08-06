import numpy as np
import pandas as pd
import os
import sys
import logging



def gettingAndCheckingWeights(weightsi):
    try:
        weights=[int(i) for i in weightsi.split(',')]
        return weights
    except:
        logging.error("expected weights array")
        print("expected weights array")
        sys.exit()

def gettingAndCheckingImpacts(impactsi):
    try:
        impacts=impactsi.split(',')
        for i in impacts:
            if not (i=='+' or i=='-'):
                logging.error("expected + or - in impact array")
                print("expected + or - in impact array")
                sys.exit()
        return impacts
    except:
        logging.error("expected impact array")
        print("expected impact array")
        sys.exit()


def checkColumns(weights, impacts, numberOfColumns):
    if (numberOfColumns-1)!=len(weights):
        logging.error("incorrect number of weights")
        print("incorrect number of weights")
        return False
    if (numberOfColumns-1)!=len(impacts):
        logging.error("incorrect number of impacts")
        print("incorrect number of impacts")
        return False
    return True
    
def normalizeData(tempDataset,numberOfColumns,weights):
    for i in range(1,numberOfColumns):
        temp=0
        for j in range(len(tempDataset)):
            temp+=tempDataset.iloc[j,i]**2
        temp**=0.5
        for j in range(len(tempDataset)):
            tempDataset.iat[j,i]=(tempDataset.iloc[j,i]/temp)*weights[i-1]
    return tempDataset

def introduceImpacts(tempDataset,numberofColumns,impacts):
    positiveSolution=(tempDataset.max().values)[1:]
    negativeSolution=(tempDataset.min().values)[1:]
    for i in range(1,numberofColumns):
        if impacts[i-1]=='-':
            positiveSolution[i-1],negativeSolution[i-1]=negativeSolution[i-1],positiveSolution[i-1]
    return positiveSolution,negativeSolution

def Topsis(dataset,numberOfColumns,weights,impacts,fileName='output.csv'):
    tempData=dataset
    tempData=normalizeData(tempData,numberOfColumns,weights)
    positiveSolution,negativeSolution=introduceImpacts(tempData,numberOfColumns,impacts)
    topsisScore=[]
    for i in range(len(tempData)):
        tempPositive,tempNegative=0,0
        for j in range(1,numberOfColumns):
            tempPositive+=(positiveSolution[j-1]-tempData.iloc[i,j])**2
            tempNegative+=(negativeSolution[j-1]-tempData.iloc[i,j])**2
        tempPositive,tempNegative=tempPositive**0.5,tempNegative**0.5
        topsisScore.append(tempNegative/(tempPositive+tempNegative))
    dataset['Topsis Score']=topsisScore
    dataset['Rank']=(dataset['Topsis Score'].rank(method='max',ascending=False))
    dataset=dataset.astype({"Rank":int})
    dataset.to_csv(fileName,index=False)

def TopsisCalc(inputf,weightsi,impactsi,outputf):
    dataset=pd.read_csv(inputf)
    numberOfColumns=len(dataset.columns.values)
    for i in range(1,numberOfColumns):
        pd.to_numeric(dataset.iloc[:,i],errors='coerce')
        dataset.iloc[:,i].fillna((dataset.iloc[:,i].mean()),inplace=True)
    weights=gettingAndCheckingWeights(weightsi)
    impacts=gettingAndCheckingImpacts(impactsi)
    if not checkColumns(weights,impacts,numberOfColumns):
        sys.exit()
    Topsis(dataset,numberOfColumns,weights,impacts,outputf)



  
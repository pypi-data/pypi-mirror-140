import numpy as np
import pandas as pd
import os
import sys
import logging


logging.basicConfig(filename='101916046-log.log',filemode='w',format='%(name)s - %(levelname)s - %(message)s')

if not len(sys.argv)>4:
    logging.error("EXPECTED 4 ARGUMENTS")
    print("EXPECTED 4 ARGUMENTS")
    sys.exit()

if not os.path.exists(sys.argv[1]):
    logging.error("FILE NOT FOUND")
    print("FILE NOT FOUND")
    sys.exit()

def handleNonNumericValues(dataset,numberOfColumns):
    for i in range(1,numberOfColumns):
        pd.to_numeric(dataset.iloc[:,i],errors='coerce')
        dataset.iloc[:,i].fillna((dataset.iloc[:,i].mean()),inplace=True)
    return dataset

def gettingAndCheckingWeights():
    try:
        weights=[int(i) for i in sys.argv[2].split(',')]
        return weights
    except:
        logging.error("expected weights array")
        print("expected weights array")
        sys.exit()

def gettingAndCheckingImpacts():
    try:
        impacts=sys.argv[3].split(',')
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
        logging.error("number of weights are not correct ")
        print("number of weights are not correct")
        return False
    if (numberOfColumns-1)!=len(impacts):
        logging.error("number of impacts is not correct")
        print("number of impacts is not correct")
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
    
    if not len(dataset.columns.values)==numberOfColumns:
        logging.error("number of columns are incorrect")
        print("number of columns are incorrect")
        sys.exit()
    
    if not checkColumns(weights,impacts,numberOfColumns):
        sys.exit()
    
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

def gettingDataFromCSV():
    dataset=pd.read_csv(sys.argv[1])

    numberOfColumns=len(dataset.columns.values)

    dataset=handleNonNumericValues(dataset,numberOfColumns)
    
    weights=gettingAndCheckingWeights()
    
    impacts=gettingAndCheckingImpacts()

    if not checkColumns(weights,impacts,numberOfColumns):
        sys.exit()
    
    if((os.path.splitext(sys.argv[4]))[1]!=".csv"):
        logging.log("expected a csv output filename")
        print("expected a csv output filename")
        sys.exit()
    if(os.path.isfile(sys.argv[4])):
        os.remove(sys.argv[4])
    
    Topsis(dataset,numberOfColumns,weights,impacts,sys.argv[4])

if __name__ == "__main__":
    gettingDataFromCSV()
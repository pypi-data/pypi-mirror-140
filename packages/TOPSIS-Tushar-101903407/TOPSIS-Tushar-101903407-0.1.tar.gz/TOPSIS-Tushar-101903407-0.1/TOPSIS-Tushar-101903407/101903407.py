from operator import truediv
import pandas as pd
import numpy as np
from topsis import Topsis
import sys
def default():
    if len(sys.argv)!=5 :
        raise Exception("please enter four parameters")
    if sys.argv[1].endswith(('.csv')):
        pass
    else:
        raise Exception("imput file should be of type - csv")
    filename=sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    outputFile=sys.argv[4]
    weights = list(map(float ,weights.split(',')))
    impacts = list(map(str ,impacts.split(',')))
    for imp in  impacts:
        if imp =='+' or imp=='-':
            pass
            
        else:
            raise Exception("impact must be positive(+) or negative (-)")
    try:
        dataset, temp_dataset = pd.read_csv(filename), pd.read_csv(filename)
    except:
        print("Input Error:File Read Error/File Not Found")
        sys.exit()
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
        raise Exception("Insufficient Weights")
    if len(impacts) != c:
        raise Exception("Insufficient Impacts")
    (rows,columns)=dataset.shape
    topsis_pipy(temp_dataset, dataset, columns, weights, impacts)
    dataset.to_csv(outputFile,index=False)

def Normalize(df, columns, weights):
    for i in range(1, columns):
        temp = 0
        for j in range(len(df)):
            temp = temp + df.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(df)):
            df.iat[j, i] = (df.iloc[j, i] / temp)*weights[i-1]

def Calc_Values(df, columns, impacts):
    ideal_best = (df.max().values)[1:]
    ideal_worst = (df.min().values)[1:]
    for i in range(1, columns):
        if impacts[i-1] == '-':
            ideal_best[i-1], ideal_worst[i-1] = ideal_worst[i-1], ideal_best[i-1]
    return ideal_best, ideal_worst

def topsis_pipy(temp_dataset, dataset, columns, weights, impacts):
    Normalize(temp_dataset, columns, weights)
    ideal_best, ideal_worst = Calc_Values(temp_dataset, columns, impacts)
    score = []
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, columns):
            temp_p = temp_p + (ideal_best[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (ideal_worst[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
    dataset['Topsis Score'] = score
    dataset['Rank'] = (dataset['Topsis Score'].rank(
        method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})
    dataset.to_csv(sys.argv[4], index=False)
if __name__ == "__main__":
    default()
import numpy as np
import pandas as pd

idealBest = []
idealWorst = []
sPlus = []
sNeg = []
sumOfIdeal = []
performanceScore = []
rank = []


def standarization(df,df2):
    for col in df:
        sq_sum  = 0.0
        for row in df[col]:
            sq_sum = sq_sum + (row*row)
        col_scaler = np.sqrt(sq_sum)
    for col in df2:
        for row in df2[col]:
            df2[col] = df2[col].replace(row,row/col_scaler)
            
def applyWeight(df2,weights):
    i = 0
    for col in df2:
        for row in df2[col]:
            df2[col] = df2[col].replace(row,row*weights[i])
        i+=1

def idealValues(df2,impacts):
    i = 0
    for col in df2:
        if(impacts[i] == '+'):
            idealBest.append(df2[col].max())
            idealWorst.append(df2[col].min())
        else:
            idealWorst.append(df2[col].max())
            idealBest.append(df2[col].min())
        i+=1
    
def euclidDistance(df2):
    for i in range(len(df2)):
        x_series = df2.iloc[i]
        j = 0
        pos = 0
        neg = 0
        for x in x_series:
            pos = pos + (x - idealBest[j])**2
            neg = neg + (x - idealWorst[j])**2
            j+=1
        sPlus.append(np.sqrt(pos))
        sNeg.append(np.sqrt(neg))
    
    for value in range(len(sPlus)):
        sumOfIdeal.append(sPlus[value] + sNeg[value])

def performance(df):
    for i in range(len(sNeg)):
        performanceScore.append(sNeg[i]/sumOfIdeal[i])
    
    temp = performanceScore.copy()
    temp.sort(reverse=True)
    
    ranking = {}
    for i in range(len(temp)):
        ranking[temp[i]] = i+1
    for i in performanceScore:
        rank.append(ranking[i])

    df['Topsis Score'] = performanceScore
    df['Rank'] = rank

    

def topsis(df, weights, impacts):

    df2 = df.copy(deep = True)
    standarization(df,df2)
    applyWeight(df2,weights)
    idealValues(df2,impacts)
    euclidDistance(df2)
    performance(df)
    return df

'''
df = pd.read_csv("101903630-data.csv")
df.drop(['Fund Name'],axis  = 1, inplace=True)
topsis(df,[1,2,3,4,1],['+','+','-','+','-'])
print(df)
'''
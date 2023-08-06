'''
Name: Garvit Jain
Roll Number: 101903079
Group: 3CO3
'''


import numpy as np
import pandas as pd

idealBest = []
idealWorst = []
s_pos = []
s_minus = []
sumOfIdeal = []
ratingScore = []
rank = []


def normalization(dataframe,dataframe2):
    for col in dataframe:
        sq_sum  = 0.0
        for row in dataframe[col]:
            sq_sum = sq_sum + (row*row)
        col_scaler = np.sqrt(sq_sum)
    for col in dataframe2:
        for row in dataframe2[col]:
            dataframe2[col] = dataframe2[col].replace(row,row/col_scaler)
            
def addWeights(dataframe2,weights):
    i = 0
    for col in dataframe2:
        for row in dataframe2[col]:
            dataframe2[col] = dataframe2[col].replace(row,row*weights[i])
        i+=1

def optimalVal(dataframe2,impacts):
    i = 0
    for col in dataframe2:
        if(impacts[i] == '+'):
            idealBest.append(dataframe2[col].max())
            idealWorst.append(dataframe2[col].min())
        else:
            idealWorst.append(dataframe2[col].max())
            idealBest.append(dataframe2[col].min())
        i+=1
    
def distance(dataframe2):
    for i in range(len(dataframe2)):
        x_series = dataframe2.iloc[i]
        j = 0
        pos = 0
        neg = 0
        for x in x_series:
            pos = pos + (x - idealBest[j])**2
            neg = neg + (x - idealWorst[j])**2
            j+=1
        s_pos.append(np.sqrt(pos))
        s_minus.append(np.sqrt(neg))
    
    for value in range(len(s_pos)):
        sumOfIdeal.append(s_pos[value] + s_minus[value])

def rating(dataframe):
    for i in range(len(s_minus)):
        ratingScore.append(s_minus[i]/sumOfIdeal[i])
    
    temp = ratingScore.copy()
    temp.sort(reverse=True)
    
    ranking = {}
    for i in range(len(temp)):
        ranking[temp[i]] = i+1
    for i in ratingScore:
        rank.append(ranking[i])

    dataframe['Topsis Score'] = ratingScore
    dataframe['Rank'] = rank

    

def topsis(dataframe, weights, impacts):

    dataframe2 = dataframe.copy(deep = True)
    normalization(dataframe,dataframe2)
    addWeights(dataframe2,weights)
    optimalVal(dataframe2,impacts)
    distance(dataframe2)
    rating(dataframe)
    return dataframe

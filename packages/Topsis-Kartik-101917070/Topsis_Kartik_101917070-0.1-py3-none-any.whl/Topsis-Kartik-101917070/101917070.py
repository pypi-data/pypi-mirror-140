#!/usr/bin/env python
# coding: utf-8


#program by kartik arora// 101917070 // cse-3
import click
import numpy as np
import pandas as pd

from re import fullmatch


def data_validations(original_df, weights, impacts):
    if original_df.shape[1] < 3:
        raise Exception('Atleast 3 Columns Required.')

    if original_df.shape[1] - 1 == len(weights) == len(impacts):
        pass

    else:
        raise Exception('Weights, Impacts and Comparison Columns must be of same length.')  

def euc(row1, row2):
    return (((row1 - row2)**2).sum())**(1/2)
    


def topsis(input_file, weights, impacts, output_file):
    
    weights = [int(w) for w in weights.split(',')]
    impacts = impacts.split(',')

    if str(input_file).endswith('.csv'):
        original_df = pd.read_csv(input_file)
    else:
        original_df = pd.read_excel(input_file)
    data_validations(original_df, weights, impacts)
    
    original_df.to_csv('101917070-data.csv', index=False)
    df = original_df.iloc[:, 1:]

    for col in df.columns:
        squared_sum = (df[col]**2).sum()
        sqrt_squared_sum = squared_sum ** (1/2)
        df[col] = df[col] / sqrt_squared_sum
        
    sm = sum(weights)
    weights = [w / sm for w in weights]
    for i in range(len(weights)):
        df.iloc[:, i] = df.iloc[:, i]*weights[i]
        
    best = []
    worst = []

    for i in range(len(impacts)):
        mn = df.iloc[:,i].min()
        mx = df.iloc[:,i].max()
        
        if impacts[i] == '+':
            best.append(mx)
            worst.append(mn)
        else:
            best.append(mn)
            worst.append(mx)
            
    best=np.array(best)
    worst=np.array(worst)

    s1 = []
    s2 = []
    for i in range(df.shape[0]):
        s1.append(euc(np.array(df.iloc[i, :]), best))
        s2.append(euc(np.array(df.iloc[i, :]), worst))

    df['s+'] = s1
    df['s-'] = s2
    df['p+'] = df['s-'] / (df['s-'] + df['s+'])

    df['rank'] = np.nan
    indices = np.argsort(df['p+'].values)[::-1]
    k = 1
    for i in indices:
        df.iloc[i, -1] = k
        k+=1

    original_df['Topsis Score'] = (df['p+']*100).round(2)
    original_df['Rank'] = df['rank'].astype(int)
    original_df.to_csv(output_file, index=False)
    
import sys
filename = sys.argv[0]
input_file = sys.argv[1]
weights=sys.argv[2]
impacts=sys.argv[3]
output_file=sys.argv[4]
    
# try:
topsis(input_file, weights, impacts, output_file)
# except Exception as e:
#     print(e)


# In[ ]:





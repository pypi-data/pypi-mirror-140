# Yoshna Marwaha , 101903502 

import math
import pandas as pd
import numpy as np
import sys
import copy

if len(sys.argv) != 5:
    print('Incorrect number of arguments')
    sys.exit()

inputData =sys.argv[1]
weights = sys.argv[2]
impacts = sys.argv[3]
output = sys.argv[4]

for i in weights:
    try:
        float(i)
    except:
        if i not in [',', '.']:
            print('Weights must be a comma separated list of numbers')
            sys.exit()
for i in impacts:
    if i not in ['+','-',',']:
        print('Impacts must be a comma separated list of +,-')
        sys.exit()

if inputData.split('.')[-1] != 'csv':
    print('Incorrect input file format')
    sys.exit()
if output.split('.')[-1] != 'csv':
    print('Incorrect output file format')
    sys.exit()

# Read input data
try:
    df = pd.read_csv(inputData)
except:
    print("File Not Found")
    sys.exit()


if len(df.columns) < 3:
    print('Input file must have at least 3 columns')
    sys.exit()

df_new = copy.deepcopy(df)
df_new = df_new.iloc[:,1:]
weights = weights.split(",")
impacts = impacts.split(",")
# print(df_new)

row = len(df_new)
col = len(df_new.columns)

for i in df_new:
    for j in df_new[i]:
        if type(j) != float:
            print('2nd to last columns must contain numeric values only')
            sys.exit()

if len(weights) != col or len(impacts) != col:
    print("Incorrect number of weights or impacts")
    sys.exit()

for i in impacts:
    if i not in ['+','-']:
        print("Incorrect impacts, they should be + or -")
        sys.exit()

arr=[0]*(col)

# Calculation  root of sum of squares
k = 0
for i in df_new:
    sum=0
    for j in df_new[i]:
        sum=sum+(float(j)*float(j))
    arr[k]=math.sqrt(sum)
    k+=1

# print(arr)


# Finding normalized values and multiplying with weights
k=0
for i in df_new:
    for j in range(0,row):
        df_new[i][j]= float(df_new[i][j]/arr[k])
        df_new[i][j]*=float(weights[k])
    k+=1

# print(df_new)

ideal_best = [0]*(col)
ideal_worst = [0]*(col)

# Calculating ideal best and ideal worst of all columns
k = 0
for i in df_new:
    if impacts[k] == "+":
        ideal_best[k] = np.max(df_new[i])
        ideal_worst[k] = np.min(df_new[i])
    if impacts[k] == "-":
        ideal_best[k] = np.min(df_new[i])
        ideal_worst[k] = np.max(df_new[i])
    k+=1

# print(ideal_best)
# print(ideal_worst)


dist_pos=list()
dist_neg=list()

# Calculating distance from ideal best and ideal worst (Euclidean distance)
for i in range(0, row):
    pos=0
    neg=0
    k= 0 
    for j in df_new:
        pos+=pow((df_new[j][i]-ideal_best[k]), 2)
        neg+=pow((df_new[j][i]-ideal_worst[k]), 2)
        k+=1
    dist_pos.append(float(pow(pos,0.5)))
    dist_neg.append(float(pow(neg,0.5)))

# print(dist_pos)
# print(dist_neg)

performance = list()

# Calculating performance score
for i in range(0, row):
    performance.append(dist_neg[i]/(dist_pos[i]+dist_neg[i]))

# print(performance)

performance_sorted=sorted(performance , reverse=True)
# print(performance_sorted)
rank = {}

for i in range(len(performance_sorted)):
    rank[performance_sorted[i]] = i+1

# print(rank)

rank_arr = list()

# Assigning rank to each performance score
for i in performance:
    rank_arr.append(rank[i])

# print(rank_arr)

df["Topsis Score"] = performance
df["Rank"] = rank_arr
print(df)
df.to_csv(output)
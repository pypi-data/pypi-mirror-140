# Name: Yugal Verma
# Batch: COE30
# Roll No: 401903007

import sys
import numpy as np
import pandas as pd
import os

class fileNotFound(Exception):
    """Base class for other exceptions"""
    pass

class wrongArgs(Exception):
    """Base class for other exceptions"""
    pass

try:
    if len(sys.argv) != 5:
        raise wrongArgs
    input_file = sys.argv[1]  
    output_file = sys.argv[4] 
    w = list(sys.argv[2].split(","))
    impact = list(sys.argv[3].split(","))
    
    if(os.path.isfile(input_file) == False):
        raise fileNotFound

    if((impact.count("+") + impact.count("-")) != len(impact)):
        print("The values of impact must be '+' or '-'")
        sys.exit(1)

except wrongArgs:
    print("Wrong Command. Usage: python file.py file.csv Weigths Impacts ResultFilename.csv")
    sys.exit(1)

except fileNotFound:
    print("File not found")
    sys.exit(1)


read_file = pd.read_excel (input_file)
read_file.to_csv ("401903007-data.csv", index = None, header=True)
df = pd.read_csv("401903007-data.csv")

if((len(w)!=len(impact)) or (len(w)!=(len(df.columns)-1))):
        print("Length of weights, impact and no of columns are not same")
        sys.exit(1)

for x in df.iloc[:,1:] :
    if df[x].dtype=='object':
        print("From 2nd to last columns must contain numeric value only")
        sys.exit(1)

n = len(df.columns)
if(n<3):
    print("Input File must contain 3 or more columns")
    sys.exit(1)

print("\nNormalized Decision Matrix: ")
df_norm = df.iloc[:,1:]/(np.sqrt(np.power(df.iloc[:,1:],2).sum(axis = 0)))
print(df_norm)

w = list(map(float,w))
print("\nWeighted Normalized Decision Matrix: ")
df_norm = df_norm * (w)
print(df_norm)

positive = (df_norm.max().values)
negative = (df_norm.min().values)

for i in range(0, len(impact)):
    if impact[i] == '-':
        positive[i], negative[i] = negative[i], positive[i]

print("\nIdeal Best: ")
print(positive)
print("\nIdeal Worst: ")
print(negative)

print("\nEuclidean Distance from ideal best")
s_positive = np.sqrt(np.power(df_norm-positive,2).sum(axis = 1))
print(s_positive)
print("\nEuclidean Distance from ideal worst")
s_negative = np.sqrt(np.power(df_norm-negative,2).sum(axis = 1))
print(s_negative)

print("\nTOPSIS score")
score = s_negative/(s_positive + s_negative)
print(score)

s_scores = sorted(score, reverse=True)
ranklist = dict()
for i in range(len(s_scores)):
    ranklist[s_scores[i]] = i+1
ranks = [ranklist[x] for x in score]

df["Topsis Score"] = score
df["Rank"] = ranks

df.to_csv(output_file)


import pandas as pd
import numpy as np
import sys

#logfile
f = open("101917205-log.txt", "a+")
if len(sys.argv) != 5:
    f.write("Incorrect number of parameters")
    f.write("\n")
    exit()

infile = sys.argv[1]

# setting the weights and impacts
weights = sys.argv[2]
w = weights.split(",")              
impact = sys.argv[3]
im = impact.split(",")
outfile = sys.argv[4]

try:
    data = pd.read_csv(infile)
except FileNotFoundError:
    f.write("File not Found")
    f.write("\n")


if len(w) != len(im):
    f.write("Different number of elements in weights and impact lists")
    f.write("\n")
    exit()

        
for i in im:
    if i != "+" and i != "-":
        f.write("Incorrect Impact values")
        f.write("\n")
        exit()

df = data.iloc[:,1:].copy(deep=True)

# Function to normalize the values
def Normalization(df,w):
    for i in range(df.shape[1]):
        total_sq_sum = 0
        
        for j in list(df.iloc[:,i]):
            total_sq_sum += j**2
        deno = total_sq_sum**0.5
        
        for ind,k in enumerate(list(df.iloc[:,i])):
            df.iloc[ind,i] = k*float(w[i])/deno

# function for calculating ideal best and ideal worst
def calcIdeal(df,im):
    ideal_best = []
    ideal_worst = []
    
    for i in range(df.shape[1]):
        if im[i] == '+':
            ideal_best.append(df.max()[i])
            ideal_worst.append(df.min()[i])
        else:
            ideal_best.append(df.min()[i])
            ideal_worst.append(df.max()[i])
            
    return ideal_best,ideal_worst


def topsisScore(df,ideal_best,ideal_worst):
    
    dist_pos = []
    dist_neg = []
    for i in range(df.shape[0]):
            dist_pos.append(np.sqrt(sum((df.iloc[i,:].values-np.array(ideal_best))**2)))
            dist_neg.append(np.sqrt(sum((df.iloc[i,:].values-np.array(ideal_worst))**2)))

    score = []
    for i in range(len(dist_pos)):
        score.append(dist_neg[i]/(dist_pos[i]+dist_neg[i]))
    
    return score

# Calling the normalization function
Normalization(df,w)
# print(df)

# Calling the calcIdeal function
ideal_best,ideal_worst = calcIdeal(df,im)
# print(ideal_best)
# print(ideal_worst)

# Calling the topsis score generator function
score = topsisScore(df,ideal_best,ideal_worst)
# print(score)

# Adding the rank and score columns in the original dataset
data['Topsis Score'] = score
data['Rank'] = (data['Topsis Score'].rank(method='max', ascending=False))
data = data.astype({"Rank": int})

print(data)
data.to_csv(outfile)
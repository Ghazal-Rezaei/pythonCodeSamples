import numpy as np
import pandas as pd
import random

# Sat1027 adjustments
Tmax = 7000
MaxClause = 1027
my_cols = ['A','B','C','D','E','F']
df = pd.read_csv('sat1027.txt', names=my_cols, sep='\s+', engine='python')

MaxVariable = 0
Tmin = 1
MaxFound = 0
MaxAlloc = np.zeros(MaxVariable)

clauses = df.values
MaxVariable = int(np.nanmax(clauses))
if abs(np.nanmin(clauses)) > MaxVariable:
    MaxVariable = int(abs(np.nanmin(clauses)))

inp = input().strip()
inp = inp.split('  ')
Allocation = np.zeros(len(inp))
for i in range(len(inp)):
    inp[i] = int(inp[i])
    if inp[i] > 0:
        Allocation[inp[i]-1] = 1
    elif inp[i] < 0:
        Allocation[inp[i]-1] = 0
for i in Allocation:
    print(int(i), end=', ')
print()
f = np.zeros(MaxClause)
for i in range(len(clauses)):
    for literal in clauses[i]:
        if literal == 0:
            break
        else:
            if literal < 0:
                f[i] = f[i] or not bool(Allocation[int(-literal)-1])
            elif literal > 0:
                f[i] = f[i] or bool(Allocation[int(literal)-1])
print(np.sum(f))
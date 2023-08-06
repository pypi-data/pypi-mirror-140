
import sys
import os.path
import pandas as pd
import topsispy as tp
import numpy as np
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

data = sys.argv[1]
weight = sys.argv[2]
impact = sys.argv[3]
output = sys.argv[4]

if(os.path.exists(data)==False):
    print("INPUT FILE NOT FOUND")
    exit(1)

if len(sys.argv)!=5:
    print("5 ARGUMENTS REQUIRED!")
    exit(1)



i=pd.read_csv(data)


if len(i.columns)<3:
    print("INPUT FILE MUST CONTAIN 3 OR MORE COLUMNS")
    exit(1)

for j in range(1,len(i.columns)):
    if(is_numeric_dtype(i.iloc[:,j])==False):
        print(" COLUMN "+i+" MUST CONATIN NUMERIC VALUES ONLY")

i = pd.read_csv(data)

weight = weight.split(',')
weight = [int(i) for i in weight]
impact = impact.split(',')

for j in range(len(impact)):
    if impact[j]=="+" or impact[j]=="-":
        continue
    else:
        print("IMPACTS MUST BE EITHER + OR -")
        exit(1)

impact = list(map(lambda x:x.replace('+','1'),impact))
impact = list(map(lambda x:x.replace('-','-1'),impact))
impact = [int(i) for i in impact]


if((len(weight)==len(impact) and len(weight)==len(i.columns)-1)==False):
    print("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same")
    exit(1)


table=i.drop(columns=['Fund Name'])
arr = table.to_numpy()
topsis = tp.topsis(arr, weight, impact)
table = pd.DataFrame(arr)
table.insert(0,"Fund Name",i["Fund Name"])
table = table.rename(columns={0:"P1",1:'P2',2:'P3',3:'P4',4:'P5'})
table['Topsis Score'] = topsis[1]
j = 1
t = topsis[1]
t = list(t)
rank={}
while len(t)!=0:
    rank[max(t)] = j
    t.remove(max(t))
    j = j + 1

table['Rank'] = table["Topsis Score"].map(rank)
table.to_csv(output)

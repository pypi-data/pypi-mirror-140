# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 15:30:32 2022

@author: N Kushal
"""

import sys
import os.path
import pandas as pd
import topsispy as tp
from pandas.api.types import is_numeric_dtype

if(os.path.exists(sys.argv[1])==False):
    print("File Doesn't Exist")
    exit(1)

if len(sys.argv)!=5:
    print("No. Of Arguments Needed - 5")
    exit(1)

i=pd.read_csv(sys.argv[1])

if len(i.columns)<3:
    print("No, of Columns Required -> Atleast 3")
    exit(1)

for j in range(1,len(i.columns)):
    if(is_numeric_dtype(i.iloc[:,j])==False):
        print("One or More Column Doesn't have all numeric values")

df = pd.read_csv("C:/Users/hp/Desktop/Topsis/101903494-data.csv")

sys.argv[2] = sys.argv[2].split(',')
sys.argv[2] = [int(i) for i in sys.argv[2]]

sys.argv[3] = sys.argv[3].split(',')

for j in range(len(sys.argv[3])):
    if sys.argv[3][j]=="+" or sys.argv[3][j]=="-":
        continue
    else:
        print("Required Symbols -> + or - ")
        exit(1)

sys.argv[3] = list(map(lambda x:x.replace('+','1'),sys.argv[3]))
sys.argv[3] = list(map(lambda x:x.replace('-','-1'),sys.argv[3]))
sys.argv[3] = [int(i) for i in sys.argv[3]]

if((len(sys.argv[2])==len(sys.argv[3]) and len(sys.argv[2])==len(i.columns)-1)==False):
    print("Reqd. Condition -No. of weights = No. of impacts = No. of columns (2 to last)")
    exit(1)

table=i.drop(columns=['Fund Name'])
arr = table.to_numpy()
topsis = tp.topsis(arr, sys.argv[2], sys.argv[3])
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

table['Rank'] = table["Topsis Score"].rank(ascending = True)
table.to_csv(sys.argv[4])
import sys
import pandas as pd
from matplotlib import pyplot as plt
import os

argumentList=sys.argv
dataset=str(argumentList[1])
nf=pd.read_csv(dataset)
df=nf.iloc[:,1:]
weights=argumentList[2]
impact=argumentList[3]

ds=df.copy()
l=[]
for i in range(0,5):
    a=0
    for c in ds.iloc[:,i]:
        a=a+pow(c,2)
    a=pow(a,0.5)
    l.append(a)

i=0
for c in ds.columns:
    val=ds[c]
    ds[c]=val/l[i]
    i=i+1

weight=weights.split(',')
d=[]
for k in weight:
    j=int(k)
    d.append(j)

i=0
for c in ds.columns:
    val=ds[c]
    ds[c]=val*d[i]
    i=i+1

impact=impact.split(',')

i=0
ii=[]
for c in ds.columns:
    m=[]
    val=ds[c]
    if impact[i]=='+':
        b=max(val)
        w=min(val)
    if impact[i]=='-':
        b=min(val)
        w=max(val)
    m.append(b)
    m.append(w)
    i=i+1
    ii.append(m)

df1=ds.copy()

i=0
for c in df1.columns:
    v=df1[c]
    df1[c]=pow(v-ii[i][0],2)
    i=i+1

df2=ds.copy()

i=0
for c in df2.columns:
    v=df2[c]
    df2[c]=pow(v-ii[i][1],2)
    i=i+1

s1=df1.sum(axis=1)
s1=pow(s1,0.5)
s2=df2.sum(axis=1)
s2=pow(s2,0.5)

pc=s2/(s1+s2)
nf['Topsis Score']=pc
nf['Rank'] = nf['Topsis Score'].rank(ascending = 0)
nf.to_csv('101903790-result.csv')
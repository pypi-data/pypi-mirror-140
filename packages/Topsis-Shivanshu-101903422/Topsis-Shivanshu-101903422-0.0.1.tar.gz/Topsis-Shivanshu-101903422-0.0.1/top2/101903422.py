import pandas as pd
import numpy as np
import sys

if(len(sys.argv)!=5):
    raise Exception('Argument count incorrect!')
    
dataset=pd.read_csv(sys.argv[1])
if(len(dataset.columns)<3):
    raise Exception("count should be > 3!")

ans=dataset.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
temp=True
for i in range(1,len(dataset.columns)):
    temp = temp & ans[i]
if(temp==False):
    raise Exception("Enter Numeric Data!")

weights=sys.argv[2]
if(weights.count(",")!=len(datset.columns)-2):
    raise Exception("Incorrect no of weights!")
weights=list(w.split(","))
for i in weights:
    if i.isalpha():
        raise Exception("Enter Numeric Weights!")
if(len(weights)!=len(dataset.columns)-1):
    raise Exception("Incorrect weight parameters count")
weights=pd.to_numeric(weights)
impact=sys.argv[3]
if(impact.count(",")!=len(dataset.columns)-2):
    raise Exception("Comma Incorrect")
lst=list(impact.split(","))
if(len(lst)!=len(dataset.columns)-1):
    raise Exception("Wrong impact count ")
for i in lst:
    if i not in ['+','-']:
        raise Exception("Wrong impact paramteres")
impact=[1 if i == '+' else -1 for i in lst]

data=dataset.copy()
columns=dataset.shape[1]
rows=dataset.shape[0]
for i in range(1,columns):
    a=np.sum((dataset.iloc[:,i])**2)
    b=np.sqrt(a)
    dataset.iloc[:,i]=dataset.iloc[:,i]/b
    dataset.iloc[:,i]=dataset.iloc[:,i]*weights[i-1]
   
columns=dataset.shape[1]
rows=dataset.shape[0]
max_list=dataset.max().values[1:]
min_list=dataset.min().values[1:]
columns=dataset.shape[1]
for i in range(1,columns):
    if impact[i-1]=='-':
        max_list[i-1],min_list[i-1]=min_list[i-1],max_list[i-1]

score=[]
for i in range(rows):
    a=dataset.iloc[i,1:]-max_list
    a=np.sqrt(np.sum(a**2))
    b=dataset.iloc[i,1:]-min_list
    b=np.sqrt(np.sum(b**2))
    score.append((b/(a+b)))


data['Topsis score']=score
data['Rank']=data['Topsis score'].rank(ascending=False)
l=data['Rank'].astype(int)
data['Rank']=l
return data

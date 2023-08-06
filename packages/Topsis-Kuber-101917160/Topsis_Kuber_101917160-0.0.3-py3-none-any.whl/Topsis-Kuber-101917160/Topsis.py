#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
import numpy as np


# In[66]:
def topsis(arr):

    # In[67]:
    if len(arr)!=5:
        print("Incorrect Number of Arguments")
        exit(0)

    if ".csv" not in arr[1]:
        print("Invalid Input file type")
        exit(0)
    if not os.path.exists(arr[1]):
        print("File not Found")
        exit(0)
    df1=pd.read_csv(arr[1])

    # In[68]:


    df=df1.iloc[:,1:]


    # In[69]:


    #weight=arr[2]
    weight=arr[2]
    impact=arr[3]

    weight=weight.split(',')


    if False in [i.isnumeric() for i in weight]:
        print("Invalid input weight string")
        exit(0)

    if(len(weight)!=df.shape[1]):
        err=f"Define {df.shape[1]-len(weight)} more" if len(weight)<df.shape[1] else f"Remove last {len(weight)-df.shape[1]}"
        print("Invalid number of weights defined. "+err)
        exit(0)
    weight=list(map(int,weight))

    for i in impact:
        if i!='+' and i!='-' and i!=',':
            print("Invalid input impact string")
            exit(0)
    impact=impact.split(',')
    if(len(impact)!=df.shape[1]):
        err=f"Define {-len(impact)+df.shape[1]} more." if len(impact)<df.shape[1] else f"Remove last {len(impact)-df.shape[1]}."
        print("Invalid number of impacts defined. "+err)
        exit(0)
    # In[77]:


    for i in df:
        sum=0
        for j in df[i]:
            sum+=j**2
        sum=sum**0.5
        df[i]=df[i]/sum


    # In[71]:


    for i in range(len(df.columns)):
        df.iloc[:,i]*=weight[i]

    # In[72]:


    vp=[]
    vn=[]
    for i in range(len(df.columns)):
        if(impact[i]=='+'):
            vp.append(df.iloc[:,i].max())
            vn.append(df.iloc[:,i].min())
        if(impact[i]=='-'):
            vp.append(df.iloc[:,i].min())
            vn.append(df.iloc[:,i].max())
    vp=np.array(vp)
    vn=np.array(vn)


    # In[73]:


    sp=[]
    sn=[]
    for i in range(df.shape[0]):
        sump=0
        sumn=0
        for j in range(df.shape[1]):
            sump+=(df.iloc[i,j]-vp[j])**2
            sumn+=(df.iloc[i,j]-vn[j])**2
        sp.append(sump**0.5)
        sn.append(sumn**0.5)
    sp=np.array(sp)
    sn=np.array(sn)


    # In[74]:


    perform=sn/(sp+sn)

    # In[75]:


    ranks=9-(perform.argsort().argsort()+1)


    # In[78]:


    df1["Topsis Score"]=perform
    df1["Rank"]=ranks
    if ".csv" not in arr[4]:
        print("Invalid Output file type")
        exit(0)  
    df1.to_csv(arr[4],index=False)


# In[ ]:

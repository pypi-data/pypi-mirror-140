import sys
import numpy as np
import os
import pandas as pd
import copy
import math

from os import path
def topsis(sourcefile,weight,impact,destinationfile):
    class myexception(Exception):
          pass
    if not (path.exists(sourcefile)):
        raise myexception(" File does not exists")
    data_frame=pd.read_csv(sourcefile)
    col=data_frame.shape
    if not col[1]>=3:
        raise myexception("Threshold of column not achieved i.e. <3")
    k=0
    for i in data_frame.columns:
        k=k+1
        for j in data_frame.index:
            if k!=1:
                val=isinstance(data_frame[i][j],int)
                val1=isinstance(data_frame[i][j],float)
                if not val and not val1:
                    raise myexception(" Values are not numeric")         
    w=[]
    wt=weight.split(',')
    for i in wt:
        k=0
        for j in i:
            if not j.isnumeric():
                if k>=1 or j!='.':
                    raise myexception("Format not correct")
                else:
                    k=k+1
        w.append(float(i))
    if len(wt)!=(col[1]-1):
        raise myexception("Number of weight required is not correct")
    imp=impact.split(',')
    for i in imp:
        if i not in {'-','+'}:
            raise myexception("Format not correct")
    if len(imp)!=col[1]-1:
        raise myexception("Number of impact required not correct")
    df=copy.deepcopy(data_frame)
    df.drop(df.columns[[0]],axis=1,inplace=True)
    a=df.to_numpy()
    b=[]
    rows=len(a)
    columns=len(a[0])
    for i in range(columns): 
        b.append(math.sqrt(sum(a[:,i]*a[:,i])))
    normalised_a=[]
    for i in range(rows):
        a1=[]
        for j in range(columns):
            a1.append(a[i][j]/b[j]*w[j])
        normalised_a.append(a1)
    normalised_a=np.array(normalised_a)

    max=normalised_a.max(axis=0)
    min=normalised_a.min(axis=0)
    v_pos=[]
    v_neg=[]
    for i in range(columns):
        if imp[i] == '-':
            v_pos.append(min[i])
            v_neg.append(max[i])
        if imp[i]=='+':
            v_pos.append(max[i])
            v_neg.append(min[i])
    s_pos=[]
    s_neg=[]
    for i in range(rows):
        temp=0
        temp1=0
        for j in range(columns):
            temp+=(normalised_a[i][j]-v_pos[j])**2
            temp1+=(normalised_a[i][j]-v_neg[j])**2
        temp=temp**0.5
        temp1=temp1**0.5
        s_neg.append(temp1)
        s_pos.append(temp)

    spos_sneg=np.add(s_pos,s_neg)

    topsis_score=[]
    for i in range(rows):
        topsis_score.append(s_neg[i]/spos_sneg[i])
    data_frame['Topsis Score']=topsis_score
    data_frame["Rank"] = data_frame["Topsis Score"].rank(ascending=False) 
    data_frame.to_csv(destinationfile,index=False)




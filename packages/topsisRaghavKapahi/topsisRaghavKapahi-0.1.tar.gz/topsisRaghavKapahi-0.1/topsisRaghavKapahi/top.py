import pandas as pd
import numpy as np
from os import path
import copy
import math
import sys
import os

    
def myfunc(mydf,w,destination,my_impact):
    
    mynewdf=copy.deepcopy(mydf)
    mynewdf.drop(mynewdf.columns[[0]],axis=1,inplace=True)
    a=mynewdf.to_numpy()
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

    maximum=normalised_a.max(axis=0)
    minimum=normalised_a.min(axis=0)

    new_pos=[]
    new_neg=[]
    for i in range(columns):
        if my_impact[i] == '-':
            new_pos.append(minimum[i])
            new_neg.append(maximum[i])
        if my_impact[i]=='+':
            new_pos.append(maximum[i])
            new_neg.append(minimum[i])
 
    s_pos=[]
    s_neg=[]
    for i in range(rows):
        temp=0
        temp1=0
        for j in range(columns):
            temp+=(normalised_a[i][j]-new_pos[j])**2
            temp1+=(normalised_a[i][j]-new_neg[j])**2
        temp=temp**0.5
        temp1=temp1**0.5
        s_neg.append(temp1)
        s_pos.append(temp)

    spos_sneg=np.add(s_pos,s_neg)

    mytop_score=[]
    for i in range(rows):
        mytop_score.append(s_neg[i]/spos_sneg[i])
 
    mydf['Topsis Score']=mytop_score
    mydf["Rank"] = mydf["Topsis Score"].rank(ascending=False) 

    mydf.to_csv(destination,index=False)
    
def topsis(src,weight,impact,destination):
   
    class myexception(Exception):
          pass
    source=src
    dest=destination
    if not (path.exists(source)):
        raise myexception("No file exists")
    if not source.endswith('.csv'):
        raise myexception("Enter proper format file only")
        
    mydf=pd.read_csv(src)
    col=mydf.shape
    if not col[1]>=3:
        raise myexception("Input file must contain greater than 3 columns")
   
    k=0
    for i in mydf.columns:
        k=k+1
        for j in mydf.index:
            if k!=1:
                val=isinstance(mydf[i][j],int)
                val1=isinstance(mydf[i][j],float)
                if not val and not val1:
                    raise myexception("NON NUMERIC VALUES")
                    
    w=[]
    my_weight=weight.split(',')
    for i in my_weight:
        k=0
        for j in i:
            if not j.isnumeric():
                if k>=1 or j!='.':
                    raise myexception("Weight Format not correct")
                else:
                    k=k+1
        w.append(float(i))

    if len(my_weight)!=(col[1]-1):
        raise myexception("Number of weight and number of columns must be equal")
        
    my_impact=impact.split(',')
    for i in my_impact:
        if i not in {'+','-'}:
            raise myexception("IMPACT FORMAT NOT CORRECT")
    if len(my_impact)!=col[1]-1:
        raise myexception("Number of impact and Number of columns must be equal")

    myfunc(mydf,w,destination,my_impact)
   



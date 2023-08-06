#Apoorv Mishra
#102083051
import pandas as pd
import numpy as np
import math
import sys
import os
def sol(a,b):
    w=a.split(',')
    for i in range(len(w)):
        if w[i]=='1' or w[i]=='1':
            w[i]='1'
    weights=[]
    for j in range(len(w)): 
        weights.append(int(w[j]))
    impact=b.split(',')
    for i in range(len(impact)):
        if impact[i]=="'+" or impact[i]=="+'":
            impact[i]='+'
        if impact[i]=="'-" or impact[i]=="-'":
            impact[i]='-'
    return [weights,impact]

def num_col(df,n_cols):
    num=[]
    for i in range(n_cols):
        if df.iloc[:,i:i+1].dtypes[0]=='float64':
            num.append(df.iloc[:,i:i+1].columns[0])
    return num
def non_num_col(df,num):
    non_num=[]
    for i in df.columns:
        if i not in num:
            non_num.append(i)
    return non_num
def weight_normalised(df,num,weights):
    sqrt_column_sum=[]
    for i in df.columns:
        if i in num:
            sqrt_column_sum.append(round(math.sqrt(df[i].pow(2).sum(axis=0)),2))
    j=0
    for i in df.columns:
        if i in num:
            df[i]=round(df[i].div(sqrt_column_sum[j]),2)
            j=j+1
    j=0
    for i in df.columns:
        if i in num:
            df[i]=round((df[i]*weights[j]),2)
            j=j+1
    return df
def V_positive(df,num,impact):
    V_pos=[]
    j=0
    for i in num:
        if impact[j]=='+':
            V_pos.append(df[i].max())
        else:
            V_pos.append(df[i].min())
        j=j+1
    return V_pos
def V_negative(df,num,impact):
    V_neg=[]
    j=0
    for i in num:
        if impact[j]=='+':
            V_neg.append(df[i].min())
        else:
            V_neg.append(df[i].max())
        j=j+1
    return V_neg
def S_positive_negative(arr,r,c,V_pos,V_neg):
    S_pos=[]
    s=0
    for i in range(r):
        for j in range(c):
            s=s+(arr[i][j]-V_pos[j])**(2)
        S_pos.append(round(math.sqrt(s),2))
        s=0
    S_neg=[]
    s=0
    for i in range(r):
        for j in range(c):
            s=s+(arr[i][j]-V_neg[j])**(2)
        S_neg.append(round(math.sqrt(s),2))
        s=0
    return [S_pos,S_neg]

def performance(r,S_pos,S_neg):
    per=[]
    for i in range(r):
        per.append(round(S_neg[i]/(S_neg[i]+S_pos[i]),5))
    return per

def Rank(score):
    n=len(score)
    ranks=[0]*n
    k=1
    for i in range(0,n):
        j=score.index(max(score))
        ranks[j]=k
        score[j] = -1
        k=k+1
    return ranks

def get_topsis_result(inputf,weightsi,impactsi,outputf):
    try:
        df=pd.read_csv(inputf)
        
        dfff=pd.read_csv(inputf)
        n_cols=len(df.columns)
        [weights,impact]=sol(weightsi,impactsi)
        for i in range(len(impact)):
            if impact[i]!="+" and impact[i]!="-":
                print("Error!")
                print("Impact is either + or -")
                sys.exit(0)
        num=num_col(df, n_cols)
        non_num=non_num_col(df, num)
        df=weight_normalised(df, num,weights)
        V_pos=V_positive(df, num,impact)
        V_neg=V_negative(df, num,impact)
        fd=df.drop(non_num,axis=1)
        arr=fd.to_numpy()
        r=len(arr)
        c=len(arr[0])
        [S_pos,S_neg]=S_positive_negative(arr, r, c, V_pos, V_neg)
        per=performance(r, S_pos, S_neg)
        fd['TOPSIS SCORE']=per
        fd['Rank'] = fd['TOPSIS SCORE'].rank(ascending=0)
        dfff['Topsis Score'] = per
        dfff['Rank'] = Rank(dfff['Topsis Score'].values.tolist())
        dfff.to_csv(outputf)
        return dfff
    except:
        print("File not found!!")
        print("Make sure your files are present in same directory of program file!!")
get_topsis_result("data.csv","1,1,1,1,1","+,+,+,+,+","out.csv")
# if __name__=='__main__':
#     main()

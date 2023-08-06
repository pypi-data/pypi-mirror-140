import pandas as pd
import sys
import math

def w_normalized(col,df,weight):
    df.iloc[:,col]=df.iloc[:,col]/(((df.iloc[:,col]**2).sum())**0.5)
    df.iloc[:,col]=df.iloc[:,col]*weight
    
def val(col,df,impact):
    if(impact=='+'):
        return [df.iloc[:,col].max(),df.iloc[:,col].min()]
    elif(impact=='-'):
        return [df.iloc[:,col].min(),df.iloc[:,col].max()]

def euclidean_distance(col,df,ideal_val):
    dis=(df.iloc[:,col]-ideal_val)**2
    return dis
    
def solve():
    num_arg=len(sys.argv)
    if(num_arg<4):
        print("Ivalid number of arguments")
        return 0

    
    try:
        df=pd.read_csv(sys.argv[1])
    except FileNotFoundError:
        print("File not Found")
        return 0
    
    weights=sys.argv[2]
    impacts=sys.argv[3]
    
    
    weights=weights.split(',')
    impacts=impacts.split(',')
    
    
    if((df.shape[1]-1)!=len(weights) or (df.shape[1]-1)!=len(impacts)):
        print("Invalid number of weights or impacts")
        return 0
    
    for i in range(1,df.shape[1]):
        w_normalized(i,df,float(weights[i-1]))
    
    ideal_val=[]
    for i in range(1,df.shape[1]):
        ideal_val.append(val(i,df,impacts[i-1]))

    s_p=[]
    s_n=[]
    for i in range(df.shape[0]):
        s_p.append(0)
        s_n.append(0)
    
    #count=0
    for i in range(1,df.shape[1]):
        tmp=euclidean_distance(i,df,ideal_val[i-1][0])
        for j in range(df.shape[0]):
            s_p[j]+=tmp[j]
    
    for i in range(1,df.shape[1]):
        tmp=euclidean_distance(i,df,ideal_val[i-1][1])
        for j in range(df.shape[0]):
            s_n[j]+=tmp[j]
    
    for i in range(df.shape[0]):
        s_p[i]=math.sqrt(s_p[i])
        s_n[i]=math.sqrt(s_n[i])
    
    topsis_score=[];
    for i in range(df.shape[0]):
        topsis_score.append(s_n[i]/(s_p[i]+s_n[i]))
        
    df['Topsis Score'] = topsis_score
    df['Rank'] = df['Topsis Score'].rank(ascending=0)


solve()

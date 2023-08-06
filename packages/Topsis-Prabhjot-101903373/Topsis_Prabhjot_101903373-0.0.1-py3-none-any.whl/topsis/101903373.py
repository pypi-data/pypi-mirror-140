# import sys
# from topsis.101903373 import topsis_puller
# l=sys.argv
# dataset=pd.read_csv(l[1])
# f=open('101903373-result.csv','w')
# f.close()
# weights=sys.argv[2]
# weightsnew=l[0].split(',')
# weights_final=[int(k) for k in weightnew]


# impact=l[0].split(',')

# topsis_puller(dataset,impact,weights_final,101903373-result.csv)


def topsis_puller(dataset,weights,impacts):
    import pandas as pd
    import numpy as np
    import sys




    if(len(sys.argv)!=5):
        raise Exception('Argument count incorrect!')
        
    df=pd.read_csv(sys.argv[1])
    if(len(df.columns)<3):
        raise Exception("count should be > 3!")

    ans=df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
    temp=True
    for i in range(1,len(df.columns)):
        temp = temp & ans[i]
    if(temp==False):
        raise Exception("Enter Numeric Data!")

    w=sys.argv[2]
    if(w.count(",")!=len(df.columns)-2):
        raise Exception("Incorrect no of weights!")
    w=list(w.split(","))
    for i in w:
        if i.isalpha():
            raise Exception("Enter Numeric Weights!")
    if(len(w)!=len(df.columns)-1):
        raise Exception("Incorrect weight parameters count")
    w=pd.to_numeric(w)
    impacts=sys.argv[3]
    if(impacts.count(",")!=len(df.columns)-2):
        raise Exception("Comma Incorrect")
    lst=list(impacts.split(","))
    if(len(lst)!=len(df.columns)-1):
        raise Exception("Wrong impact count ")
    for i in lst:
        if i not in ['+','-']:
            raise Exception("Wrong impact paramteres")
    impacts=[1 if i == '+' else -1 for i in lst]
    weights=w
    impact=impacts
    dataset=df
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
    data.to_csv(sys.argv[4],index=False)
    return data


    



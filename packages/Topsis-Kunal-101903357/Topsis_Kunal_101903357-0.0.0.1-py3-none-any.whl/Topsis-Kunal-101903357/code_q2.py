def func(df,w,impacts):
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
    df.to_csv("101903357-data.csv",index=False)

    col1=pd.DataFrame(df['Fund Name'])
    df.drop("Fund Name",inplace=True,axis=1)

    import topsispy as tp2
    a = df.values.tolist()
    x = tp2.topsis(a, w, impacts)
    df["Topsis Score"] =  x[1]
    df['Rank']=df['Topsis Score'].rank(ascending=False)
    new_dataset=pd.concat([col1,df],axis=1)
    new_dataset.to_csv(sys.argv[4],index=False)
    return new_dataset
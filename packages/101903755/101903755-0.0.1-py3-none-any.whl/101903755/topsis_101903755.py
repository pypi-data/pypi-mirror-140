import pandas as pd
import numpy as np
import sys
def topsis():
    if(len(sys.argv)!=5):
        raise Exception('Incorrect Number of Args')

    dataset=pd.read_csv(sys.argv[1])

    if(len(dataset.columns)<3):
        raise Exception("Column count not equal 3")

    ans=dataset.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
    temp=True
    for i in range(1,len(dataset.columns)):
        temp = temp & ans[i]
    if(temp==False):
        raise Exception("Not Non numeric Data")

    l=sys.argv[2]
    if(l.count(",")!=len(dataset.columns)-2):
        raise Exception("Comma Incorrect")
    l=list(l.split(","))
    for i in l:
        if i.isalpha():
            raise Exception("Weights not numeric")
    if(len(l)!=len(dataset.columns)-1):
        raise Exception("Incorrect weight parameters count")
    l=pd.to_numeric(l)
    imp=sys.argv[3]
    if(imp.count(",")!=len(dataset.columns)-2):
        raise Exception("Comma Incorrect")
    ll=list(imp.split(","))
    if(len(ll)!=len(dataset.columns)-1):
        raise Exception("Wrong impact count ")
    for i in ll:
        if i not in ['+','-']:
            raise Exception("Wrong impact paramteres")
    impacts=[1 if i == '+' else -1 for i in ll]
    dataset.to_csv(sys.argv[4],index=False)

    col1=pd.DataFrame(dataset['Fund Name'])
    dataset.drop("Fund Name",inplace=True,axis=1)

    import topsispy as tp2
    a = dataset.values.tolist()
    t = tp2.topsis(a, l, impacts)
    dataset["Topsis Score"] =  t[1]
    dataset['Rank']=dataset['Topsis Score'].rank(ascending=False)
    new_dataset=pd.concat([col1,dataset],axis=1)
    new_dataset.to_csv(sys.argv[4],index=False)


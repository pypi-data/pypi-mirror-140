import pandas as pd
import numpy as np
import topsispy as tp
import sys

def topsis(src,w,s,finaldf):
    df = pd.read_csv(src)
    if(len(df.columns) < 3):
        raise Exception('File must have 3 or more columns')

    if(w.count(',')!=(len(df.columns)-2)):
        raise Exception("Commas incorrect")
    w = w.split(",")
    if((len(w)!=(len(df.columns)-1))):
        raise Exception("Weights parameters are incorrect!")
    for i in w:
        if i.isalpha():
            raise Exception("Wrong weights!")
    w = pd.to_numeric(w)

    if(s.count(',')!=(len(df.columns)-2)):
        raise Exception("Commas incorrect")
    s = s.split(",")
    if(len(s)!=len(df.columns)-1):
        raise Exception("Wrong impacts!")

    for i in s:
        if i not in ['+', '-']:
            raise Exception("Wrong impacts!")
    s = [1 if i=='+' else -1 for i in s]

    df2 = df.drop(df.columns[0], axis=1)
    vals = df2.values.tolist()
    top = tp.topsis(vals, w, s)
    df['Topsis_Score'] = top[1]
    df['Rank'] = df['Topsis_Score'].rank(ascending=False)
    df.to_csv(finaldf, index=False)

# if __name__=='__main__':
#     topsis(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
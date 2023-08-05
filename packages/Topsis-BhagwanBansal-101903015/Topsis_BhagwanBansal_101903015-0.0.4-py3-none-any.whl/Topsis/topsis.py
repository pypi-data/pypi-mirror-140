from traceback import print_tb
import pandas as pd
import numpy as np
import sys

class NoOfCols(Exception):
    def __init__(self,message):
        self.message = message
class Error(Exception):
    def __init__(self,message):
        self.message = message

def Topsis(arg1,arg2,arg3,arg4):
    try:
        df1 = pd.read_csv(arg1)
        weight = arg2
        impact = arg3
        df = df1.iloc[:,1:]
        col = df.columns
        if int(len(col)) != (int(len(weight))):
            raise Error("No of columns and weight must be equal")
        if int(len(col)) != (int(len(impact))):
            raise Error("No of columns and impacts must be equal")
    except NoOfCols as err1:
        print(err1.message)
    except Error as err2:
        print(err2.message)
    v_p = []
    v_n = []
    p = []
    for i in col:
        rmse = np.sqrt(sum(np.square(df[i])))
        df[i] = df[i]/rmse
        df[i] = df[i]*float((weight[list(col).index(i)]))
        if(impact[list(col).index(i)]) == '+':
            v_p.append(max(df[i]))
            v_n.append(min(df[i]))
        else:
            v_p.append(min(df[i]))
            v_n.append(max(df[i]))
    for i in range(0,len(df)):
        s_p = 0
        s_n = 0
        for j in range(0,len(col)):
            s_p += np.square(float(df.iloc[i,j]-v_p[j]))
            s_n += np.square(float(df.iloc[i,j]-v_n[j]))
        s_p = np.sqrt(s_p)
        s_n = np.sqrt(s_n)
        p.append(s_n/(s_p + s_n))
    df1["Topsis Score"] = p
    df1["Rank"] = df1["Topsis Score"].rank()
    df1.to_csv(arg4,index=False)


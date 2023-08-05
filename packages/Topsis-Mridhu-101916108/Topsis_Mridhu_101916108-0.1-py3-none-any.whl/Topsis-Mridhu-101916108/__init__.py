import os
import sys
import pandas as pd 
import numpy as np
import pandas as pd
def topsis(inp,whts,impcts,res):
    try:
        with open(inp, 'r') as fl:
            file=pd.read_csv(fl)
    except FileNotFoundError:
        print("File not found")
        exit()

    DF=pd.DataFrame(data=file)

    Weg = list(whts.split(","))
    Imp = list(impcts.split(","))
    ncol = len(DF.columns)

    dict1 = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '+': True, '*': True,'-': True, '=': True}
    dict2 = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '*': True, '=': True}

    def char_check(new_list, punct_dict):
        for item in new_list:
            for char in item:
                if char in punct_dict:
                    return False

    def string_check(comma_check_list, punct_dict):
        for string in comma_check_list:
            new_list = string.split(",")
            if char_check(new_list, punct_dict) == False:
                print("comma separated value required")
                exit()

    string_check(whts, dict1)
    string_check(impcts, dict2)

    if ncol<3:
        print("If number of columns less than 3, refer your data.")
        exit()

    if len(Imp) != (ncol-1):
        print("number of entered values in impacts should be same as number of columns.")
        exit()

    if len(Weg) != (ncol-1):
        print("number of entered values in weights should be same as number of columns.")
        exit()

    ls = {'-','+'}
    if set(Imp) != {'-','+'} and set(Imp) != {'+','-'} and set(Imp) != {'-'} and set(Imp) != {'+'}:
        print(r"Impacts should be either '+' or '-'.")
        exit()

    for index,row in DF.iterrows():
        try:
            float(row['P1'])
            float(row['P2'])
            float(row['P3'])
            float(row['P4'])
            float(row['P5'])
        except:
            DF.drop(index,inplace=True)
    DF["P1"] = pd.to_numeric(DF["P1"], downcast="float")
    DF["P2"] = pd.to_numeric(DF["P2"], downcast="float")
    DF["P3"] = pd.to_numeric(DF["P3"], downcast="float")
    DF["P4"] = pd.to_numeric(DF["P4"], downcast="float")
    DF["P5"] = pd.to_numeric(DF["P5"], downcast="float")
    DF1 = DF.copy(deep=True)
    def Normalize(DF, nCol, Weg):
        for i in range(1, nCol):
            temp = 0
            for j in range(len(DF)):
                temp = temp + DF.iloc[j, i]**2
            temp = temp**0.5
            for j in range(len(DF)):
                DF.iat[j, i] = (float(DF.iloc[j, i])) / float(temp)*float(Weg[i-2])

    def Calc_Values(df, ncol, Weg):
        p_sln = (DF.max().values)[1:]
        n_sln = (DF.min().values)[1:]
        for i in range(1, ncol):
            if Imp[i-2] == '-':
                p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
        return p_sln, n_sln

    Normalize(DF,ncol,Weg)
    p_sln, n_sln = Calc_Values(DF, ncol, Imp)
    score = []
    pp = []
    nn = []

    for i in range(len(DF)):
        temp_p, temp_n = 0, 0
        for j in range(1, ncol):
            temp_p = temp_p + (p_sln[j-1] - DF.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - DF.iloc[i, j])**2
        temp_p, temp_n = temp_p*0.5, temp_n*0.5
        score.append(temp_n/(temp_p + temp_n))
        nn.append(temp_n)
        pp.append(temp_p)


    DF1['Topsis Score'] = score
    DF1['Rank'] = (DF1['Topsis Score'].rank(method='max', ascending=False))
    DF1 = DF1.astype({"Rank": int})
    DF1.to_csv(res,index=False)
    return DF1

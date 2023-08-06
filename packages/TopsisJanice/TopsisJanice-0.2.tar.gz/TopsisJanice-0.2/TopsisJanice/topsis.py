import pandas as pd
import numpy as np
import copy
import math
import os
import sys

def topsis(input,weights,impact,output):
    class customexception(Exception):
        pass
    try:
        try:
            weights = list(map(float, weights.split(',')))
            impacts = list(map(str, impact.split(',')))
        except:
            print('Impacts and weights must be separated by ‘,’')
            exit('0')

        if not input.endswith('.csv'):
            raise customexception('Only .csv format is supported')

        df1 = pd.read_csv(input)

        col=len(df1.columns)
        if col<3:
            raise customexception('Input file must contain three or more columns')

        if (len(weights) != (col - 1)) or (len(impacts) !=col-1) :
            raise customexception("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.")

        for char in impacts:
            if char not in ('+', '-'):
                raise customexception('Impacts must be either + or -')

    except Exception as e:
        print(e)
    else:
        df = copy.deepcopy(df1)
        df.drop(df.columns[[0]], axis=1, inplace=True)

        for i in df.columns:
            for j in df.index:
                if not(isinstance(df[i][j], int)) and not(isinstance(df[i][j], float)):
                    raise customexception("Must contain numeric values only")

        rows = len(df)
        cols = len(df.columns)

        sqrtl = []
        for i in range(0, cols):
            sum = 0
            for j in range(0, rows):
                sum = sum + (df.iloc[j, i] * df.iloc[j, i])
            temp = math.sqrt(sum)
            sqrtl.append(temp)

        for i in range(0, cols):
            for j in range(0, rows):
                df.iloc[j, i] = df.iloc[j, i] / sqrtl[i]

        wt=weights
        for i in range(0, cols):
            for j in range(0, rows):
                df.iloc[j, i] = df.iloc[j, i] * wt[i]

        wt_df = np.array(df)
        maximum = wt_df.max(axis=0)
        minimum = wt_df.min(axis=0)

        pos = []
        neg = []
        for i in range(0, cols):
            if impacts[i] == '+':
                pos.append(maximum[i])
                neg.append(minimum[i])
            else:
                pos.append(minimum[i])
                neg.append(maximum[i])

        s_pos = []
        s_neg = []
        for i in range(0, rows):
            temp = 0
            temp1 = 0
            for j in range(0, cols):
                temp += (df.iloc[i, j] - pos[j]) ** 2
                temp1 += (df.iloc[i, j] - neg[j]) ** 2
            temp = temp ** 0.5
            temp1 = temp1 ** 0.5
            s_neg.append(temp1)
            s_pos.append(temp)

        performance = []
        for i in range(0, len(s_pos)):
            performance.append(s_neg[i] / (s_pos[i] + s_neg[i]))

        df1['Topsis_Score'] = performance
        df1["Rank"] = df1["Topsis_Score"].rank(ascending=False)
        df1['Rank'] = df1['Rank'].astype(int)
        df1.to_csv(output, index=False)

# if __name__ == '__main__':
#     class customexception(Exception):
#         pass
#     n=len(sys.argv)
#     try:
#         if n!=5:
#             raise customexception('Incorrect number of parameters')
#     except Exception as e:
#         print(e)
#     else:
#         topsis(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
#


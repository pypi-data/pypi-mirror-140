import pandas as pd
import numpy as np
import copy
import math
import os
import sys

def topsis(input,wts,impact,output):
    class customexception(Exception):
        pass
    try:
        try:
            wts = list(map(float, wts.split(',')))
            impts = list(map(str, impact.split(',')))
        except:
            raise customexception('• Impacts and weights must be separated by ‘,’ (comma).')
            exit('0')

        if not input.endswith('.csv'):
            raise customexception('• Only .csv format is supported')

        drfr1 = pd.read_csv(input)

        col=len(drfr1.columns)
        if col<3:
            raise customexception('• Input file must contain three or more columns')

        if (len(wts) != (col - 1)) or (len(impts) !=col-1) :
            raise customexception("• Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.")

        for chr in impts:
            if chr not in ('+', '-'):
                raise customexception('• Impacts must be either + or -')

    except Exception as e:
        raise customexception(e)
    else:
        drfr = copy.deepcopy(drfr1)
        drfr.drop(drfr.columns[[0]], axis=1, inplace=True)

        for i in drfr.columns:
            for j in drfr.index:
                if not(isinstance(drfr[i][j], int)) and not(isinstance(drfr[i][j], float)):
                    raise customexception("• Must contain numeric values only")

        rws = len(drfr)
        cols = len(drfr.columns)

        sqrtl = []
        for i in range(0, cols):
            sum = 0
            for j in range(0, rws):
                sum = sum + (drfr.iloc[j, i] * drfr.iloc[j, i])
            tmp = math.sqrt(sum)
            sqrtl.append(tmp)

        for i in range(0, cols):
            for j in range(0, rws):
                drfr.iloc[j, i] = drfr.iloc[j, i] / sqrtl[i]

        wt=wts
        for i in range(0, cols):
            for j in range(0, rws):
                drfr.iloc[j, i] = drfr.iloc[j, i] * wt[i]

        wt_drfr = np.array(drfr)
        maximum = wt_drfr.max(axis=0)
        minimum = wt_drfr.min(axis=0)

        positive = []
        negitive = []
        for i in range(0, cols):
            if impts[i] == '+':
                positive.append(maximum[i])
                negitive.append(minimum[i])
            else:
                positive.append(minimum[i])
                negitive.append(maximum[i])

        s_pos = []
        s_neg = []
        for i in range(0, rws):
            tmp = 0
            tmp1 = 0
            for j in range(0, cols):
                tmp += (drfr.iloc[i, j] - positive[j]) ** 2
                tmp1 += (drfr.iloc[i, j] - negitive[j]) ** 2
            tmp = tmp ** 0.5
            tmp1 = tmp1 ** 0.5
            s_neg.append(tmp1)
            s_pos.append(tmp)

        performance = []
        for i in range(0, len(s_pos)):
            performance.append(s_neg[i] / (s_pos[i] + s_neg[i]))

        drfr1['Topsis_Score'] = performance
        drfr1["Rank"] = drfr1["Topsis_Score"].rank(ascending=False)
        drfr1['Rank'] = drfr1['Rank'].astype(int)
        drfr1.to_csv(output, index=False)

if __name__ == '__main__':
    class customexception(Exception):
        pass
    n=len(sys.argv)
    try:
        if n!=5:
            raise customexception('Incorrect number of parameters')
    except Exception as e:
        raise customexception(e)
    else:
        topsis(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
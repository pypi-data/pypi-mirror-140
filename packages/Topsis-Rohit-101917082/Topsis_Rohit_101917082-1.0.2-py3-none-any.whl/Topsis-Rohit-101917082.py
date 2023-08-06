import numpy as np
import pandas as pd
import math
import copy


def topsis(file, wt, imp):
    try:
        top = file
        finl = copy.deepcopy(top)
    except:
        print('Error! File not Found')
        return 0
    if top.shape[1] >= 3:
        for col in top.columns[1:]:
            try:
                pd.to_numeric(top[col])
            except:
                print("Error! Not all the columns after 2nd are numeric")
        we = list(wt.split(','))
        I = list(imp.split(','))
        w = []
        for i in we:
            w.append(float(i))
        if top.shape[1] - 1 == len(w) and top.shape[1] - 1 == len(I):
            list1 = []
            for col in top.columns[1:]:
                num = 0
                for row in top[col]:
                    num = num + row * row
                list1.append(math.sqrt(num))
            k = 1
            for i in range(top.shape[0]):
                for j in range(1, top.shape[1]):
                    top.iloc[i, j] = top.iloc[i, j] / list1[j - 1]
            for i in range(top.shape[0]):
                for j in range(1, top.shape[1]):
                    top.iloc[i, j] = top.iloc[i, j] * w[j - 1]
            best = []
            worst = []
            k = 0
            # print(I)
            for col in top.columns[1:]:
                if I[k] == '-':
                    best.append(top[col].min())
                    worst.append(top[col].max())
                elif I[k] == '+':
                    best.append(top[col].max())
                    worst.append(top[col].min())
                else:
                    print("Error! Impacts must be either +ve or -ve.")
                    return 0
                k = k + 1
            E_best = []
            E_worst = []
            for i in range(top.shape[0]):
                sq_best = 0
                sq_worst = 0
                diff = 0
                diff_best = 0
                diff_worst = 0
                for j in range(1, top.shape[1]):
                    # print(i, j)
                    diff = top.iloc[i, j] - best[j - 1]
                    diff_best = diff * diff
                    diff = top.iloc[i, j] - worst[j - 1]
                    diff_worst = diff * diff
                    sq_best = sq_best + diff_best
                    sq_worst = sq_worst + diff_worst
                E_best.append(math.sqrt(sq_best))
                E_worst.append(math.sqrt(sq_worst))
            P_score = []
            for i in range(top.shape[0]):
                P_score.append(E_worst[i] / (E_worst[i] + E_best[i]))
            finl['Topsis Score'] = P_score
            finl['Rank'] = finl['Topsis Score'].rank(ascending=False)
            return finl

        else:
            print("Error! Number of weights, number of impacts or number of columns are not same")
            print("Error! Impacts and weights must be separated by ‘,’ (comma).")
            return 0
    else:
        print("Error! Input file must have more than 3 columns.")
        return 0

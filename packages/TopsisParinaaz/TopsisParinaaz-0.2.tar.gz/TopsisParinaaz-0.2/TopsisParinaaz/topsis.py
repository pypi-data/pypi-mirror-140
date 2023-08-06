import sys
import math
import pandas as pd
import numpy as np

import copy
def topsis(src,weights,impacts,result):

    try:
        weights = list(map(float, weights.split(',')))
        impacts = list(map(str, impacts.split(',')))
    except:
        print('Separate weights and impacts with commas')
        exit(0)

    for ch in impacts:
        if ch not in ('+', '-'):
            print('Incorrect impacts')
            exit(0)

    try:
        df1 = pd.read_csv(src)
    except:
        print('File not found')
        exit(0)

    if len(list(df1.columns)) < 3:
        print('Less than 3 columns not allowed')
        exit(0)

    df1.drop(df1.columns[[0]], axis=1, inplace=True)
    df=copy.deepcopy(df1)
    for i in df.columns:
        for j in df.index:
            if not (isinstance(df[i][j], int)) and not (isinstance(df[i][j], float)):
                print("Must contain numeric values only")
                exit(0)

    cols = df.shape[1]
    rows = df.shape[0]

    if len(weights) != cols or len(impacts) != cols:
        print("Incorrect number of weights or impacts")
        exit(0)

    df = df.values.astype(float)

    sq = [0] * cols
    for i in range(0, rows):
        for j in range(0, cols):
            sq[j] += (df[i][j] * df[i][j])
    for j in range(cols):
        sq[j] = math.sqrt(sq[j])

    for i in range(rows):
        for j in range(cols):
            df[i][j] = (df[i][j] / sq[j])
            df[i][j] = df[i][j] * weights[j]

    max = np.max(df, axis=0)
    min = np.min(df, axis=0)

    v_pos = []
    v_neg = []

    for i in range(0, cols):
        if impacts[i] == "-":
            v_pos.append(min[i])
            v_neg.append(max[i])
        else:
            v_pos.append(max[i])
            v_neg.append(min[i])

    s_pos = []
    s_neg = []
    for i in range(0, rows):
        temp = 0
        temp1 = 0
        for j in range(0, cols):
            temp = temp + (df[i][j] - v_pos[j]) * (df[i][j] - v_pos[j])
            temp1 = temp1 + ((df[i][j] - v_neg[j]) * (df[i][j] - v_neg[j]))
        temp = math.sqrt(temp)
        temp1 = math.sqrt(temp1)
        s_neg.append(temp1)
        s_pos.append(temp)

    score = []
    for i in range(rows):
        score.append(s_neg[i] / (s_pos[i] + s_neg[i]))

    rank = [0] * len(score)
    for i, x in enumerate(sorted(range(len(score)), key=lambda y: score[y])):
        rank[x] = len(score) - i

    df1['Topsis Score'] = score
    df1['Rank'] = rank

    res = pd.DataFrame(df1)
    res.to_csv(result, index=False)

#
# if __name__ == "__main__":
#
#     if len(sys.argv) != 5:
#         print('Incorrect number of parameters')
#         exit(0)
#     topsis(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
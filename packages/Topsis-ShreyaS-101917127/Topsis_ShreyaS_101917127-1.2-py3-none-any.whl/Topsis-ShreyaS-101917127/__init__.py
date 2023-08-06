import sys
import math as m
import pandas as pd
import numpy as np

def topsis(file, wei, impa, result):

    try:
        d = pd.read_csv(file)
    except:
        print('File not found')
        exit(0)

    if len(d.columns) < 3:
        print('Less than 3 columns not allowed')
        exit(0)

    try:
        weight = wei.split(',')
        weights = list(map(float, weight))
        impact =impa.split(',')
        impacts = list(map(str, impact))
    except:
        print('The weights and impacts are not comma-separated')
        exit(0)


    for ch in impacts:
        if not (ch == '+' or ch == '-'):
            print('The impacts are Incorrect')
            exit(0)

    df = d.drop(['Fund Name'], axis=1)

    c = len(df.columns)

    if len(impacts) != c or len(weights) != c:
        print("The number of weights, impacts and columns are unequal")
        exit(0)

    r, c = df.shape
    df = df.values.astype(float)

    # sum of squares
    sumSq = [0] * (c)
    for i in range(0, c):
        for j in range(0, r):
            sumSq[i] = sumSq[i] + (df[j][i] * df[j][i])

    # root of sum of squares
    for j in range(c):
        sumSq[j] = m.sqrt(sumSq[j])

    # normalized decision matrix
    for i in range(c):
        for j in range(r):
            df[j][i] = df[j][i] / sumSq[i]

    # weight assignment
    for i in range(c):
        for j in range(r):
             df[j][i] = df[j][i] * weights[i]

    # ideal best and ideal worst
    maximum = np.max(df, axis=0)
    minimum = np.min(df, axis=0)

    for i in range(c):
        if impacts[i] == '-':
             minimum[i], maximum[i] = maximum[i], minimum[i]

    # euclidean distances
    EuclideanPlus = [0] * r
    EuclideanMin = [0] * r

    for i in range(r):
        s = 0
        for j in range(c):
            s = s + ((df[i][j] - maximum[j]) * (df[i][j] - maximum[j]))
            EuclideanPlus[i] = m.sqrt(s)

    for i in range(r):
        s = 0
        for j in range(c):
            s = s + ((df[i][j] - minimum[j]) * (df[i][j] - minimum[j]))
            EuclideanMin[i] = m.sqrt(s)


    # Performance score
    Perform = {}
    for i in range(r):
            Perform[i + 1] = EuclideanMin[i] / (EuclideanMin[i] + EuclideanPlus[i])

    #rank assignment
    P = list(Perform.values())
    FinalP = sorted(P, reverse=True)
    Rank = {}

    for value in P:
        Rank[(FinalP.index(value) + 1)] = value
    rank = Rank
    ans = d
    ans['Topsis Score'] = list(rank.values())
    ans['Rank'] = list(rank.keys())
    res = pd.DataFrame(ans)
    res.to_csv(result, index=False)
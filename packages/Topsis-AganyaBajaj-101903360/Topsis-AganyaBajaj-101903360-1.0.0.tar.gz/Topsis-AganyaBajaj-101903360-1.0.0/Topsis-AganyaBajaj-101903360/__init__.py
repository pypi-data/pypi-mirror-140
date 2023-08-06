# 101903360 Aganya Bajaj

import sys
import math
import pandas as pd
import numpy as np
from os import path


def topsis(filename, weights, impacts, outname):

    df = pd.read_csv(filename)

    cols = df.columns[1:]

    original = df.copy(deep=True)

    for i in cols:
        norm = 0
        for x in df[i]:
            norm += x**2
        norm = math.sqrt(norm)

        df[i] /= norm

    best = []
    worst = []

    weights = list(map(int, weights))
    weights = pd.Series(data=weights, index=cols)
    impacts = pd.Series(data=impacts, index=cols)

    for i in cols:
        df[i] *= weights[i] / sum(weights)

        if impacts[i] == '+':
            best.append(df[i].max())
            worst.append(df[i].min())
        else:
            best.append(df[i].min())
            worst.append(df[i].max())

    splus = []
    sminus = []

    for _, x in df.iterrows():
        a = 0
        b = 0
        for i in range(1, len(x)):
            a += (x[i] - best[i - 1])**2
            b += (x[i] - worst[i - 1])**2

        splus.append(math.sqrt(a))
        sminus.append(math.sqrt(b))

    p = []

    for i, x in df.iterrows():
        p.append(sminus[i] / (sminus[i] + splus[i]))

    original["Topsis Score"] = p
    original["Rank"] = original["Topsis Score"].rank(ascending=False)

    original.to_csv(outname)


def checkReq():
    args = sys.argv
    if len(args) != 5:
        print("Incorrect number of parameters")
        return

    filename = args[1]
    weights = args[2]
    impacts = args[3]
    outname = args[4]

    if not path.exists(filename):
        print("Input file not found")
        return

    df = pd.read_csv(filename)

    weights = weights.split(",")
    impacts = impacts.split(",")

    for x in weights:
        if (not x.isdigit):
            print("Incorrect input in weights")
            return

    for x in impacts:
        if (x != '+' and x != '-'):
            print("Incorrect input in impacts")
            return

    cols = df.columns[1:]

    if len(cols) < 3:
        print("Columns less than 3")
        return

    if len(cols) != len(weights):
        print("Number of columns not equal to number of weights")

    if len(weights) != len(impacts):
        print("Number of impacts not equal to number of weights")
        return

    for i in cols:
        if not pd.api.types.is_numeric_dtype(df[i]):
            print(f"{i}th column is non-numeric")
            return

    topsis(filename, weights, impacts, outname)


if __name__ == "__main__":
    checkReq()

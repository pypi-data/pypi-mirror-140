import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def func(a,b,c):
    infile = a
    w = b
    im = c
    w = [float(i) for i in w.split(",")]
    im = im.split(",")
    try:
        topsis = pd.read_csv(infile)
    except FileNotFoundError:
        exit()

    if len(w) != len(im):
        print("Number of elements in both the lists must be same")
        print("\n")
        exit()

    for i in im:
        if i != "+" and i != "-":
            print("Incorrect Impact values")
            print("\n")
            exit()

    s = topsis.copy(deep=True)
    n = topsis.shape[0]
    m = topsis.shape[1]
    if m < 3:
        print("File must contain three or more columns")
        print("\n")
        exit()

    if len(im) != m - 1:
        print("Impact must be seperated by ,")
        print("\n")
        exit()

    d = ((topsis.iloc[:, 1:] ** 2).sum()) ** 0.5
    for i in range(n):
        s.iloc[i, 1:] = s.iloc[i, 1:] / d

    for i in range(m - 1):
        s.iloc[:, i + 1] = s.iloc[:, i + 1] * float(w[i])

    vp = []
    vn = []
    for i in range(m - 1):
        if im[i] == "+":
            vp.append(s.iloc[:, i + 1].max())
            vn.append(s.iloc[:, i + 1].min())
        else:
            vp.append(s.iloc[:, i + 1].min())
            vn.append(s.iloc[:, i + 1].max())

    sp = []
    for i in range(n):
        sp.append((((s.iloc[i, 1:] - vp) ** 2).sum()) ** 0.5)

    sn = []
    for i in range(n):
        sn.append((((s.iloc[i, 1:] - vn) ** 2).sum()) ** 0.5)

    p = []
    for i in range(n):
        p.append(sn[i] / (sn[i] + sp[i]))

    topsis['Topsis Score'] = p

    topsis['Rank'] = topsis['Topsis Score'].rank(ascending=0)
    print(topsis)
    # topsis.to_csv(outfile)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

# logfile
f = open("102083045-log.txt", "a+")
if len(sys.argv) != 5:
    f.write("Incorrect number of parameters")
    f.write("\n")
    exit()

infile = sys.argv[1]
weights = sys.argv[2]
w = weights.split(",")
impact = sys.argv[3]
im = impact.split(",")
outfile = sys.argv[4]
try:
    topsis = pd.read_csv(infile)
except FileNotFoundError:
    f.write("File not Found")
    f.write("\n")

if len(w) != len(im):
    f.write("Number of elements in both the lists must be same")
    f.write("\n")
    exit()

for i in im:
    if i != "+" and i != "-":
        f.write("Incorrect Impact values")
        f.write("\n")
        exit()

s = topsis.copy(deep=True)
n = topsis.shape[0]
m = topsis.shape[1]
if m < 3:
    f.write("File must contain three or more columns")
    f.write("\n")
    exit()

if len(im) != m - 1:
    f.write("Impact must be seperated by ,")
    f.write("\n")
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
topsis.to_csv(outfile)

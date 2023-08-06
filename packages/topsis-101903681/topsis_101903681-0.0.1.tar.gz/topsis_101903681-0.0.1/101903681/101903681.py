import sys
from os import path
import pandas as pd
import numpy as np
import scipy.stats as ss


def topsis(input_file, weight, impact, output_file):
    n = len(input_file.columns)
    length = len(input_file)
    df = input_file
    for j in range(1, n):
        s = np.sqrt(np.square(df.iloc[:, j]).sum())
        p = df.iloc[:, j] / s
        p = p * weight[j - 1]
        m = df.columns[j]
        df[m] = p

    v_best = []
    v_worst = []
    for j in range(1, n):
        if impact[j - 1] == "+":
            ma = max(df.iloc[:, j])
            v_best.append(ma)
            mi = min(df.iloc[:, j])
            v_worst.append(mi)
        elif impact[j - 1] == "-":
            ma = max(df.iloc[:, j])
            v_worst.append(ma)
            mi = min(df.iloc[:, j])
            v_best.append(mi)

    s_plus = []
    s_minus = []
    for j in range(0, length):
        maxi = 0
        mini = 0
        for k in range(1, n):
            maxi += (np.square(df.iloc[j, k] - v_best[k - 1]))
            mini += (np.square(df.iloc[j, k] - v_worst[k - 1]))
        s_plus.append(np.sqrt(maxi))
        s_minus.append(np.sqrt(mini))
    performance = []
    for j in range(0, length):
        performance.append(s_minus[j] / (s_minus[j] + s_plus[j]))
    rank = ss.rankdata(performance)
    rank1 = len(performance) - rank.astype(int) + 1
    d = input_file
    d["Topsis Score"] = performance
    d["Rank"] = rank1
    d.to_csv(output_file)

def check_input():
    if len(sys.argv) != 5:
        print("Enter correct number of parameters")
        exit(0)
    file_name = pd.read_csv(sys.argv[1])
    inp = sys.argv[1]
    weight = sys.argv[2]
    impact = sys.argv[3]
    output = sys.argv[4]


    if not (sys.argv[1].endswith(".csv") or sys.argv[4].endswith(".csv")):
        print("Wrong inputs entered")
        exit(0)
    if not (path.exists(inp) or path.exists(output)):
        print("File not Found")
        exit(0)
    if len(file_name.columns) <= 3:
        print("Columns less than expected")
        exit(0)
    k = 0
    for i in file_name.columns:
        k = k + 1
        for j in file_name.index:
            if k != 1:
                val = isinstance(file_name[i][j], int)
                val1 = isinstance(file_name[i][j], float)
                if not val and not val1:
                    print(f"Value is not numeric in {k} column")
                    exit(0)

    n = len(file_name.columns)
    impacts = impact.split(",")
    weights = weight.split(",")

    for j in range(len(weights)):
        weights[j] = float(weights[j])
    if not (len(weights) == len(impacts) == n - 1):
        print("No. of weights, no. of impacts, no. of columns are not equal")
        exit(0)

    if not ("+" or "-" in impacts):
        print("impact must contain only + or -")
        exit(0)
    if len(impacts) <= 1 and len(weights) <= 1:
        print("Either weights or impacts are not comma separated")
        exit(0)
    topsis(file_name, weights, impacts, output)

check_input()
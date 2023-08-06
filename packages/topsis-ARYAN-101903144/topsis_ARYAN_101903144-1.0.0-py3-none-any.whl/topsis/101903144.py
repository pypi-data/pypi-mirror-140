import sys
import math
import pandas as pd
import numpy as np

def valid(i):
    if i > 5:
        print('more input than required')
        exit(0)
    elif i < 5:
        print('less input than required')
        exit(0)
    try:
        w = list(map(float, sys.argv[2].split(',')))
        imp = list(map(str, sys.argv[3].split(',')))
    except:
        print('Separate w and imp with commas')
        exit(0)

    for ch in imp:
        if ch not in ('+', '-'):
            print('Incorrect imp')
            exit(0)

    result = sys.argv[4]

    try:
        dataCSV = pd.read_csv(sys.argv[1])
    except:
        print('File not found')
        exit(0)

    if len(list(dataCSV.columns)) < 3:
        print('Less than 3 columns not allowed')
        exit(0)
    return  dataCSV,w,imp,result
def finder(r,c,data,R_M_S,w,totw):
    for i in range(0, r):
        for j in range(0, c):
            R_M_S[j] += (data[i][j] * data[i][j])

    for j in range(c):
        R_M_S[j] = math.sqrt(R_M_S[j])

    for i in range(c):
        w[i] /= totw

    for i in range(r):
        for j in range(c):
            data[i][j] = (data[i][j] / R_M_S[j]) * w[j]
def euclid(data,mxD,mD,r,c):
    euclidPlus = []
    euclidMinus = []
    performance = {}
    for i in range(r):
        sum = 0
        for j in range(c):
            sum += pow((data[i][j] - mxD[j]), 2)
        euclidPlus.append(float(pow(sum, 0.5)))

    for i in range(r):
        sum = 0
        for j in range(c):
            sum += pow((data[i][j] - mD[j]), 2)
        euclidMinus.append(float(pow(sum, 0.5)))
    for i in range(r):
        performance[i + 1] = euclidMinus[i] / (euclidMinus[i] + euclidPlus[i])
    return performance

def main():
    i=len(sys.argv)
    dataCSV,w,imp,result=valid(i)

    data = dataCSV.drop(['Fund Name'],axis=1)
    r=data.shape[0]
    c=data.shape[1]
    if len(w) != c :
        print("invalid no. of w")
        exit(0)
    if len(imp) != c:
        print("invalid no. imp")
        exit(0)
    data = data.values.astype(float)
    totw = np.sum(w)

    R_M_S = [0] * (c)
    finder(r, c, data, R_M_S, w, totw)
    mxD = np.amax(data, axis=0)
    mD = np.amin(data, axis=0)

    for i in range(len(imp)):
        if (imp[i] == '-'):
            temp = mxD[i]
            mxD[i] = mD[i]
            mD[i] = temp
    performance=euclid(data,mxD,mD,r,c)

    p = list(performance.values())
    pFinal = sorted(list(performance.values()), reverse=True)

    R_A_N_K = {}

    for val in p:
        R_A_N_K[(pFinal.index(val) + 1)] = val

    O_U_T = dataCSV
    O_U_T['Topsis Score'] = list(R_A_N_K.values())
    O_U_T['R_A_N_K'] = list(R_A_N_K.keys())

    res = pd.DataFrame(O_U_T)
    res.to_csv(result, index=False)


if __name__ == "__main__":
    main()

import pandas as pd 
import numpy as np
import os 
import sys



def floater(a):  # .astype() can be used but is not reliable
    b = []
    for i in a:
        try:
            ix = []
            for j in i:
                ix.append(float(j))
        except:
            ix = float(i)
            pass
        b.append(ix)
    b = np.array(b)
    return b


def normalize(matrix, r, n, m):
    for j in range(m):
        sq = np.sqrt(sum(matrix[:, j]**2))
        for i in range(n):
            r[i, j] = matrix[i, j]/sq
    return r


def weight_product(matrix, weight):
    r = matrix*weight
    return r


def calc_ideal_best_worst(sign, matrix, n, m):
    ideal_worst = []
    ideal_best = []
    for i in range(m):
        if sign[i] == 1:
            ideal_worst.append(min(matrix[:, i]))
            ideal_best.append(max(matrix[:, i]))
        else:
            ideal_worst.append(max(matrix[:, i]))
            ideal_best.append(min(matrix[:, i]))
    return (ideal_worst, ideal_best)


def euclidean_distance(matrix, ideal_worst, ideal_best, n, m):
    diw = (matrix - ideal_worst)**2
    dib = (matrix - ideal_best)**2
    dw = []
    db = []
    for i in range(n):
        dw.append(sum(diw[i, :])**0.5)
        db.append(sum(dib[i, :])**0.5)
    dw = np.array(dw)
    db = np.array(db)
    return (dw, db)


def performance_score(distance_best, distance_worst, n, m):
    score = []
    score = distance_worst/(distance_best + distance_worst)
    return score


def topsis(a, w, sign):
    a = floater(a)
    # print(a)
    n = len(a)
    # print(n)
    # print(len(a[0]))
    m = len(a[0])
    # print('n:', n, '\nm:', m)
    r = np.empty((n, m), np.float64)
    r = normalize(a, r, n, m)
    t = weight_product(r, w)
    (ideal_worst, ideal_best) = calc_ideal_best_worst(sign, t, n, m)
    (distance_worst, distance_best) = euclidean_distance(
        t, ideal_worst, ideal_best, n, m)
    score = performance_score(distance_best, distance_worst, n, m)
    return (score)
    # returns a tupple with index of best data point as first element and score array(numpy) as the other



if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Wrong Number of args')
        print('Input should be like - \n '
              'python <program.py> <InputDataFile> <Weights> <Impacts> <ResultFileName>]')
    else:
        file_path = sys.argv[1]
        try:
            if os.path.exists(file_path):
                print('Path exist')
        except OSError as err:
            print(err.reason)
            exit(1)
        df = pd.read_excel(file_path)
    
        if((df.dtypes[0])!=object):
            print("first column should be object column")
            exit(1)
        if (len(df.columns)<3):
            print("Too less columns")
            exit(1)
        newdf=df.iloc[1:,1:]
        try:
            newdf = newdf.apply(pd.to_numeric)
        except OSError as error:
            print(error.reason)
            exit(1)
        for i in newdf.dtypes:
            if(i not in ['int64','float64']):
                print("column ",i," not an integer type")
                exit(1)
        a = newdf.values
        arg2 = sys.argv[2]
        arg3 = sys.argv[3]
        w = arg2.strip('][').split(',')
        w = list(map(float, w))
        s = arg3.strip('][').split(',')
 
        impact=[]
        for i in s:
            if(i=='+'):
                impact.append(1)
            elif(i=='-'):
                impact.append(-1)
            else:
                print("impact Signs should be + or - only ")
                exit(1)

        impact = list(map(int, impact))
        if(len(w)!=len(impact)):
            print("Length of weights and impackts are not equal")
            exit(1)
    
        res = pd.Series(topsis(a, w, impact))
        rank=res.rank(ascending=False)
        a=np.array(['Topsis Score'])
        df["Topsis Score"]=np.append(a,res)
        p=np.array(['Rank'])
        df["Rank"]=np.append(p,rank)
        df.to_csv(sys.argv[4],index=False,header=False)
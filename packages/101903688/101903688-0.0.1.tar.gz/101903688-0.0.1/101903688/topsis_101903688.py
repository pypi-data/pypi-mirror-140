import sys
import os
import pandas as pd
import math
import numpy as np


class Topsiscls:
    def __init__(self, filename):
        data = pd.read_csv(filename)
        self.d = data.iloc[:, 1:].values
        print(self.d)
        self.features = len(self.d[0])
        self.samples = len(self.d)

    def fun1(self, a):
        return a[1]

    def fun2(self, a):
        return a[0]

    def calculatetopsis(self, w=None, im=None):
        d = self.d
        features = self.features
        samples = self.samples
        if w == None:
            w = [1] * features
        if im == None:
            im = ["+"] * features
        ideal_best = []
        ideal_worst = []
        for i in range(0, features):
            k = math.sqrt(sum(d[:, i] * d[:, i]))
            max1 = 0
            min1 = 1
            for j in range(0, samples):
                d[j, i] = (d[j, i] / k) * w[i]
                if d[j, i] > max1:
                    max1 = d[j, i]
                if d[j, i] < min1:
                    min1 = d[j, i]
            if im[i] == "+":
                ideal_best.append(max1)
                ideal_worst.append(min1)
            else:
                ideal_best.append(min1)
                ideal_worst.append(max1)
        p = []
        for i in range(0, samples):
            a = math.sqrt(sum((d[i] - ideal_worst) * (d[i] - ideal_worst)))
            b = math.sqrt(sum((d[i] - ideal_best) * (d[i] - ideal_best)))
            lst = []
            lst.append(i)
            lst.append(a / (a + b))
            p.append(lst)
        p.sort(key=self.fun1)
        rank = 1
        for i in range(samples - 1, -1, -1):
            p[i].append(rank)
            rank += 1
        p.sort(key=self.fun2)
        return p


def calc_Topsis(filename, w, im):
    ob = Topsiscls(filename)
    res = ob.calculatetopsis(w, im)
    return res


def main():
    argu = sys.argv
    # read_file = pd.read_excel(argu[1])
    # read_file.to_csv(r'101903688-data.csv', index=None, header=True)
    # argu[1]=r"101903688-data.csv"
    print(argu[1])
    length = len(argu)
    if length == 5:
        weights = list(map(int, argu[2].split(',')))
        impacts = argu[3].split(',')
        topsis_res = calc_Topsis(argu[1], weights, impacts)
        print(topsis_res)
        rank = []
        score = []
        for i in topsis_res:
            score.append(i[1])
            rank.append(i[2])
        df1 = pd.read_csv("101903688-data.csv")
        print(df1)
        df1["topsis_score"] = score
        df1["rank"] = rank
        print(df1)
        df1.to_csv(argu[4], index=False)
    else:
        print("wrong Parameters")


if __name__ == '__main__':
    main()


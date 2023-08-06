import sys
import numpy as np
import pandas as pd

def topsis_function(df, w, impacts):
    x = df.iloc[:, 1:6]

    # Root of sum of squares
    rosos = []
    for i in range(0, x.shape[1]):
        sum = 0
        for j in range(0, x.shape[0]):
            sum += pow(x.loc[j].iat[i], 2)
        fin = pow(sum, 0.5)
        rosos.append(fin)

    for i in range(0, x.shape[1]):
        for j in range(0, x.shape[0]):
            x.loc[j].iat[i] = (x.loc[j].iat[i])/rosos[i]

    weights_final = []
    for i in range(len(w)):
        weights_final.append(int(w[i]))

    for i in range(0, x.shape[1]):
        for j in range(0, x.shape[0]):
            x.loc[j].iat[i] = (x.loc[j].iat[i])*weights_final[i]

    # + -> Max is best
    # - -> Min is best
    vj_plus = [] # Ideal best
    vj_minus = [] # Ideal worst
    for i in range(0, x.shape[1]):
        if (impacts[i] == '+'):
            vj_plus.append(x.iloc[:, i].max())
            vj_minus.append(x.iloc[:, i].min())
        else:
            vj_plus.append(x.iloc[:, i].min())
            vj_minus.append(x.iloc[:, i].max())

    si_plus = []
    for i in range(0, x.shape[0]):
        sum = 0
        for j in range(0, x.shape[1]):
            sum += pow(((x.loc[i].iat[j])-(vj_plus[j])), 2)
        fin = pow(sum, 0.5)
        si_plus.append(fin)

    si_minus = []
    for i in range(0, x.shape[0]):
        sum = 0
        for j in range(0, x.shape[1]):
            sum += pow(((x.loc[i].iat[j])-(vj_minus[j])), 2)
        fin = pow(sum, 0.5)
        si_minus.append(fin)

    si = []
    for i in range(len(si_plus)):
        si.append(si_plus[i]+si_minus[i])

    pi = []
    for i in range(len(si_plus)):
        pi.append(si_minus[i]/si[i])

    df["Topsis Score"] = pi

    df["Rank"] = df["Topsis Score"].rank(ascending=True)
    
    return df

df = pd.read_csv(sys.argv[1])

weights = sys.argv[2]
w = weights.split(",")

imp = sys.argv[3]
impacts = imp.split(",")

result_file_name = sys.argv[4]

df = topsis_function(df, w, impacts)
df.to_csv(result_file_name, index=False)
import pandas as pd
import numpy as np
import scipy.stats as ss

def dist(a, b):
    m = a-b
    m = m.pow(2)
    val = m.sum()
    val = np.sqrt(val)
    return val

def topsis(df, weights, impacts):
    w = weights
    if(w.count(',')!=(len(df.columns)-2)):
        raise Exception("Commas incorrect")
    w = w.split(",")
    if((len(w)!=(len(df.columns)-1))):
        raise Exception("Weights parameters are incorrect!")
    for i in w:
        if i.isalpha():
            raise Exception("Wrong weights!")
    w = [float(i) for i in w]

    s = impacts
    if(s.count(',')!=(len(df.columns)-2)):
        raise Exception("Commas incorrect")
    s = s.split(",")
    if(len(s)!=len(df.columns)-1):
        raise Exception("Wrong impacts!")

    for i in s:
        if i not in ['+', '-']:
            raise Exception("Wrong impacts!")
    new_df = df.drop(df.columns[0], axis = 1)
    new_df = new_df.astype(float)
    sq = new_df.pow(2).sum(axis = 0)
    sq = np.sqrt(sq)
    sq = np.array(sq)
    new_df = new_df/sq.reshape(1, len(new_df.columns))

    weight = np.array(w)
    weight.astype(float)

    new_df = new_df*weight.reshape(1, len(new_df.columns))
    # assuming max value as ideal best and min value as worst
    vmax = new_df.max()
    vmin = new_df.min()
    for i in range(0, len(new_df.columns)):
        if s[i] == '-':
            temp = vmax[i]
            vmax[i] = vmin[i]
            vmin[i] = temp
    distances_sl = []
    distances_sh = []
    for i in range(0,new_df.shape[0]):
        distances_sl.append(dist(new_df.iloc[i,:], vmin))
        distances_sh.append(dist(new_df.iloc[i, :], vmax))

    p_score = []
    for i in range(0, len(distances_sh)):
        val = distances_sl[i]/(distances_sl[i]+distances_sh[i])
        p_score.append(val)
    p_score = np.array(p_score)
    rank = ss.rankdata(p_score*-1)
    p_score = pd.DataFrame(p_score)
    p_score.columns = ['Performance Score']
    rank = pd.DataFrame(rank.astype(int))
    rank.columns = ["Rank"]
    af = [df, p_score, rank]
    final = pd.concat(af, axis = 1)

    return final

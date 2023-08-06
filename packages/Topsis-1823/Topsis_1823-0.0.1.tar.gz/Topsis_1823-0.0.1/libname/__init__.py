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
    
    new_Datafile=df.drop(df.columns[0], axis = 1)

    new_Datafile=new_Datafile.astype(float)

    sq_root = new_Datafile.pow(2).sum(axis = 0)

    sq_root = np.sqrt(sq_root)

    sq_root = np.array(sq_root)

    new_Datafile = new_Datafile/sq_root.reshape(1, len(new_Datafile.columns))

    weights = np.array(w)

    weights.astype(float)

    new_Datafile=new_Datafile*weights.reshape(1,len(new_Datafile.columns))

    ver_max=new_Datafile.max()

    ver_min=new_Datafile.min()

    for i in range(0,len(new_Datafile.columns())):
        if s[i] == '-':
            temp=ver_min[i]
            ver_min[i]=ver_max[i]
            ver_max=temp

    Dist_best=[]
    Dist_wors=[]

    for i in range(0,new_Datafile.shape[0]):
        Dist_best.append(dist(new_Datafile.iloc[i,:], ver_max))
        Dist_wors.append(dist(new_Datafile.iloc[i,:], ver_min))

    p_score=[]

    for i in range(0, len(Dist_best)):
        val = Dist_wors[i]/(Dist_wors[i]+Dist_best[i])
        p_score.append(val)

    p_score = np.array(p_score)

    rank = ss.rankdata(p_score*-1)

    p_score = pd.DataFrame(p_score)
    p_score.columns = ['Performance Score']

    rank = pd.DataFrame(rank.astype(int))
    rank.columns = ["Rank"]

    final_output = [df, p_score, rank]

    final = pd.concat(final_output, axis = 1)
    return final
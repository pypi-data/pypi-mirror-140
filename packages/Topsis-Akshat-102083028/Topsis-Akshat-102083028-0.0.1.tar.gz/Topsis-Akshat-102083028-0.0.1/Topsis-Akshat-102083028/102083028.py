import sys
import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np


def top():
    if len(sys.argv) != 5:
        raise Exception("Incorrect no of Paramaters")
    try:
        top_data = pd.read_csv(sys.argv[1])
    except FileNotFoundError:
        print("The File does not exist in the Directory")
        exit(1)

    if(len(top_data.columns) < 3):
        raise Exception("ERROR: number of columns in Dataframe less than 3")
    if(top_data.columns[0].find("Name") == -1):
        raise Exception("THE FIRST COLUMN Is INCORRECT")

    weight = sys.argv[2].split(',')
    weight = [int(i) for i in weight]
    imp = sys.argv[3].split(',')
    impact = [i for i in imp if i == '+' or i == '-']
    if(len(imp) != len(impact)):
        raise Exception("Enter only + and - for impact separated by ','")
    # print(weight)
    # print(impact)
    if(len(weight) != top_data.shape[1]-1):
        raise Exception("INCORRECT WEIGHT ENTRIES")
    if(len(impact) != top_data.shape[1]-1):
        raise Exception("INCORRECT IMPACT ENTRIES")

    # weight=[2,2,3,3,4]
    # impact=['+','-','+','-','+']
    topdata = top_data.iloc[:, 1:]
    # print(topdata.columns)
    for i in topdata.columns:
        if (is_numeric_dtype(topdata[i])):
            continue
        else:
            raise Exception("Error: NON NUMERIC Column")

    for i, kilo in topdata.iteritems():
        f = np.sqrt(np.sum(np.square(kilo)))
        topdata[i] = (kilo/f)
# print(topdata)
    topdata = topdata*weight
# print(topdata)

# calculating idealbest and worst
    idealbest = topdata.max(axis=0).values
    idealworst = topdata.min(axis=0).values
#print(idealbest, idealworst)
    for kj in range(len(topdata.columns.values)):
        if impact[kj] == '-':
            idealbest[kj], idealworst[kj] = idealworst[kj], idealbest[kj]
#print(idealbest, idealworst)

    for j, sk in topdata.iterrows():
        spos = np.sqrt(np.sum(np.square(sk.values-idealbest)))
        sneg = np.sqrt(np.sum(np.square(sk.values-idealworst)))
        top_data.at[j, 'Topsis Score'] = sneg/(sneg+spos)
    top_data['Rank'] = top_data['Topsis Score'].rank(
        method='max', ascending=False)
    top_data.to_csv(sys.argv[4])


if __name__ == "__main__":
    top()

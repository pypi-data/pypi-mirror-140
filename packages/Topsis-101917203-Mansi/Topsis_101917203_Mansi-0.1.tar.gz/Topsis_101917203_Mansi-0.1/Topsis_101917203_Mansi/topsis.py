import pandas as pd
import numpy as np

def topsis(filename,weights,impacts):

    #Step1 - Getting Decison Matrix
    dataset = pd.read_csv(filename)
    dataset = dataset.values[:,1:]
    dm = pd.DataFrame(dataset).to_numpy(dtype = float)

    #Step2 - Calculating Normalised Decison Matrix
    numRows = len(dm)
    numCols = len(dm[0])

    #getting denominator
    denom = []
    for j in range(numCols):
        sum = 0
        for i in range(numRows):
           sum = sum + (dm[i][j] ** 2)
        value = sum ** 0.5
        denom.append(value)
    
    #updating matrix
    for i in range(numRows):
        for j in range(numCols):
            dm[i][j] = dm[i][j] / denom[j]
    
    
    #Step3 - Calculating weighted Normalised Matrix
    for j in range(numCols):
        for i in range(numRows):
            dm[i][j] = dm[i][j] * float(weights[j])
    
    #Step4 - Calulating ideal best and worst for each column
    maxx = np.amax(dm, axis=0)
    minn = np.amin(dm, axis=0)
    vbest = []
    vworst = []
    for i in range(numCols):
        if impacts[i] == 1:
            vbest.append(maxx[i])
            vworst.append(minn[i])
        elif impacts[i] == 0:
            vbest.append(minn[i])
            vworst.append(maxx[i])
    
    #Step5(a) - Calculating Eucledian Distance from ideal(best)
    dbest = []
    for i in range(numRows):
        sum1 = 0
        for j in range(numCols):
            sum1 = sum1 + ((dm[i][j] - vbest[j]) ** 2)
        dist1 = sum1 ** 0.5
        dbest.append(dist1)
            
    #Step5(b) - Calculating Eucledian Distance from ideal(worst)
    dworst = []
    for i in range(numRows):
        sum2 = 0
        for j in range(numCols):
            sum2 = sum2 + ((dm[i][j] - vworst[j]) ** 2)
        dist2 = sum2 ** 0.5
        dworst.append(dist2)
    
    #Step6 - Calculating Performance
    perf = []
    for i in range(numRows):
        p = dworst[i] / (dworst[i] + dbest[i])
        perf.append(round(p,7))
    
    #Result - Printing rank and best model
    rank = perf.copy()
    rank.sort(reverse=True)
    
    print("Index       Score       Rank")
    for i in range(numRows):
        print(str(i+1)+"       "+str(perf[i])+"       "+str(rank.index(perf[i]) + 1))
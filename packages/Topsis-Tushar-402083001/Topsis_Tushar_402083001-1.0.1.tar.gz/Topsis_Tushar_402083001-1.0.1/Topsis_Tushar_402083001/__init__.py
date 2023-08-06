import pandas as pd
import math as ma
import copy

def topsis(inputFile, weights, impacts, outputFile = None):
    if isinstance(inputFile, pd.core.frame.DataFrame):
        df = inputFile 
    else:
        inpFile = inputFile.split(".")
        if inpFile[-1] != "csv":
            print("Wrong extension! Required file extension: .csv \n")
            return

        try:
            df = pd.read_csv(inputFile)
        except:
            print(f"{inputFile} not found! \n")
            return
    
    if len(df.columns) < 3:
        print(f"{inputFile} must contain 3 or more columns/features \n")
        return
    
    temp = copy.deepcopy(df)

    cols = df.columns
    cols = cols[1:]

    for i in cols:
        if not pd.api.types.is_numeric_dtype(df[i]):
            print(f"{i} column of given file is  non-numeric \n")
            return

    for i in weights:
        if not(i.isdigit() or i == ","):
            print("Weights must separated by , \n")
            return

    for i in impacts:
        if i not in ["+", "-", ","]:
            print("Illegal impacts, \n")
            return

    weights = weights.split(",")
    impacts = impacts.split(",")

    if len(weights) != len(cols):
        print(f"No of weights and No of columns in {inputFile}  must be same! \n")
        return

    if len(impacts) != len(cols):
        print(f"No of impacts and No of columns in {inputFile}  must be same! \n")
        return
        
    weights = pd.Series(data = weights, index = cols, dtype = float)
    impacts = pd.Series(data = impacts, index = cols)

    for i in impacts:
        if not(i == "+" or i == "-"):
            print("Impacts must be either + or - \n")
            return

    ideal_best = pd.Series(dtype = float)
    ideal_worst = pd.Series(dtype = float)

    for i in cols:
        df[i] /= (ma.sqrt((df[i] ** 2).sum()))
        df[i] *= weights[i] / sum(weights)

        if impacts[i] == "+":
            ideal_best[i] = df[i].max()
            ideal_worst[i] = df[i].min()
        else:
            ideal_best[i] = df[i].min()
            ideal_worst[i] = df[i].max()

    for i in df.index:
        dist_iw = 0
        dist_ib = 0
        for j in cols:
            dist_iw += ((df.loc[i, j] - ideal_worst[j]) ** 2)
            dist_ib += ((df.loc[i, j] - ideal_best[j]) ** 2)
        dist_ib = ma.sqrt(dist_ib)
        dist_iw = ma.sqrt(dist_iw)
        df.loc[i, "Topsis Score"] = dist_iw / (dist_ib + dist_iw)

    for i in cols:
        df[i] = temp[i]

    df["Rank"] = df["Topsis Score"].rank(ascending = False)

    if not outputFile == None:
        outFile = outputFile.split(".")
        if outFile[-1] != "csv":
            print("Output file has wrong extension")
            return
        df.to_csv(outputFile, index = False)

    return df
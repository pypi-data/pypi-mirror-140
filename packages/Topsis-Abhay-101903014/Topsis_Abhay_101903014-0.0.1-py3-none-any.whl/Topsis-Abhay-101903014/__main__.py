import numpy as np
import pandas as pd
import sys
from os.path import exists
from pandas.api.types import is_numeric_dtype

def main():
    #Check for number of parameters
    if len(sys.argv)!=5:
        print("Error:\nWrong Number of Parameters")
        print("\nPlease use the format:")
        print("python <programName> <input.csv> <weights array> <impacts array> <output.csv>\n\n")
        exit(1)

    #Check if file exists and is readable...
    if not exists(sys.argv[1]):
        print("Error: input file " + sys.argv[1] + " does not exist")
        exit(1)

    #Load data from csv file
    data = pd.read_csv(sys.argv[1])
    
    #Get Rows and Columns in input file
    rows,cols = data.shape

    if(cols<3):
        print("Input file must contain at least 3 columns")
        exit(1)

    #Values from 2nd column onwards...shud be numeric only...for each row
    df=data[data.columns[1:cols]]
    for i,j in df.iterrows():
        if(not is_numeric_dtype(j)):
            print("Error: All Values in Data shud be numeric " )
            print(df)
            exit(1)

    #Validations:
    rawweights = sys.argv[2].split(',')
    #Check for number of values
    if (len(rawweights) !=  cols-1):
        print("Error: entered weights are not same as columns in data")
        exit(1)

    #Check for numeric values
    if not all(i.isnumeric() for i in rawweights):
        print("Error: Weights has to be numeric")
        exit(1)

    weights = [int(i) for i in rawweights]
    #Check for numeric positive values
    if not all(i>0 for i in weights):
        print("Error: Weights has to be non-zero")
        exit(1)

    impacts = sys.argv[3].split(',')

    #Check for number of values
    if (len(impacts) != cols-1):
        print("Error: entered impacts are not same as columns in data")
        exit(1)

    #Check for + and -
    if not all(i=="+" or i=="-" for i in impacts):
        print("Error: Impact values can only be + or -")
        exit(1)

    best = np.zeros(cols-1)
    worst = np.zeros(cols-1)

    #Start:
    odata=data.copy()   #Keeping a copy of original data

    #Step 1: Vector Normalization
    for i in range(cols-1):
        data.iloc[:,i+1] = data.iloc[:,i+1]/np.sqrt(sum(data.iloc[:, i+1] ** 2))

    #Step 2: Assign Weights
    for i in range(cols-1):
        data.iloc[:,i+1] = data.iloc[:,i+1]*weights[i]

    #Step 3: Calculate Ideal Best and Ideal Worst
    for i in range(cols-1):
        if(impacts[i]==-1):
            best[i] = data.iloc[:,i+1].min()
            worst[i] = data.iloc[:,i+1].max()
        else:
            worst[i] = data.iloc[:, i + 1].min()
            best[i] = data.iloc[:, i + 1].max()
    
    #Step 4: Calculate Euclidean distance
    dis_best=np.zeros(rows)
    dis_worst=np.zeros(rows)

    for i in range(rows):
        dis_best[i] =np.linalg.norm(best - pd.Series(data.iloc[i, 1:cols]))
        dis_worst[i] = np.linalg.norm(worst - pd.Series(data.iloc[i, 1:cols]))

    #initialize new column with 0 values
    odata['Topsis Score']=np.zeros(rows)

    #Step 5: Add Score to data for output
    for i in range(rows):
        odata.iloc[i, cols]=dis_worst[i]/(dis_worst[i]+dis_best[i])

    #Get Rank Based on Topsis Score and add to output data
    odata['Rank'] = odata['Topsis Score'].rank()

    #Store output to the csv file
    odata.to_csv(sys.argv[4], index=False)

#If calling directly - execute main function
if __name__ == "__main__":
    main()
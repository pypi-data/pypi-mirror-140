from enum import unique
import sys
import pandas as pd
import numpy as np
import pandas.api.types as ptypes

# Calculate ideal best and ideal worst
def Calc_Values(topsis, ncols, impacts):
    # print("Hello")
    p_sln = (topsis.max().values)[1:]
    n_sln = (topsis.min().values)[1:]
    for i in range(1, ncols):
        if impacts[i-1] == '-':
            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
    return p_sln, n_sln



def normalise(topsis, ncols, weights):
    for i in range(1, ncols):
            temp = 0
            # Calculating Root of Sum of squares of a particular column
            for j in range(len(topsis)):
                temp = temp + topsis.iloc[j, i]**2
            temp = temp**0.5
            # Weighted Normalizing a element
            for j in range(len(topsis)):
                topsis.iat[j, i] = (topsis.iloc[j, i] / temp)*weights[i-1]
    # print(topsis)




def main():
    if(len(sys.argv)!=5):
        print("Invalid number of arguments")
        sys.exit(1)

    try:
        topsis = pd.read_csv(sys.argv[1])    
    except FileNotFoundError:
        print("File not Found")
        sys.exit(1)

    ncols = len(topsis.columns)

    if(len(topsis.columns) < 3):
        print("Number of columns are less than 3")
        sys.exit(1)
    # if(not (assert all(ptypes.is_numeric_dtype(topsis[col]) for col in topsis.columns))):
    #     print("Columns are not numeric")

    weights = list(map(int, sys.argv[2].strip().split(',')))
    impacts = sys.argv[3].split(',')
    if(len(weights)!=len(impacts) or len(weights)!=len(topsis.columns)-1):
        print("number of columns in input don't match or are not comma seperated")
        sys.exit(1)

    impacts_array = np.array(impacts)
    impacts_array = np.unique(impacts_array)
    # print(impacts_array)
    impact = list(impacts_array)
    # print(impact)
    if(impact != ['+','-']):
        print("Invalid Impacts")
        sys.exit(1)

    normalise(topsis, ncols, weights)
    # print("Hello")

    # Calculating positive and negative values
    p_sln, n_sln = Calc_Values(topsis, ncols, impacts)
    # print(p_sln, n_sln)
    # calculating topsis score
    score = [] # Topsis score

    # Calculating Topsis score for each row
    for i in range(len(topsis)):
        temp_p, temp_n = 0, 0
        for j in range(1, ncols):
            temp_p = temp_p + (p_sln[j-1] - topsis.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - topsis.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))

    # Appending new columns in dataset
    topsis['Topsis Score'] = score

    # calculating the rank according to topsis score
    topsis['Rank'] = (topsis['Topsis Score'].rank(method='max', ascending=False))
    topsis = topsis.astype({"Rank": int})
    topsis.to_csv("101903122-output.csv", index=None)

if __name__ == "__main__":
    main()
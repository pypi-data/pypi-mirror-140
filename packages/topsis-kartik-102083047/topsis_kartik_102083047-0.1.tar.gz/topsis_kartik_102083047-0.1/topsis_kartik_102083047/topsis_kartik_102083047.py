# Name : Rahul Kapoor
# Roll Number : 101903508

import pandas as pd
import os
import sys


def main():
    if len(sys.argv) != 5:
        print("ERROR : incorrect number of parameters")
        sys.exit(1)

    elif not os.path.isfile(sys.argv[1]):
        print(f"ERROR : {sys.argv[1]} Don't exist!!")
        sys.exit(1)

    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        print(f"ERROR : csv '{sys.argv[1]}' not found!!")
        sys.exit(1)

    else:
        dataset, temp_dataset = pd.read_csv(
            sys.argv[1]), pd.read_csv(sys.argv[1])
        nCol = len(temp_dataset.columns.values)

        # less then 3 columns in input dataset
        if nCol < 3:
            print("ERROR :less then 3 columns")
            exit(1)

        # Handeling non-numeric value
        for i in range(1, nCol):
            pd.to_numeric(dataset.iloc[:, i], errors='coerce')
            dataset.iloc[:, i].fillna(
                (dataset.iloc[:, i].mean()), inplace=True)

        # Handling errors of weighted and impact arrays
        try:
            weights = [int(i) for i in sys.argv[2].split(',')]
        except:
            print("ERROR : Weights not correct")
            sys.exit(1)
        impact = sys.argv[3].split(',')
        for i in impact:
            if not (i == '+' or i == '-'):
                print("ERROR : Incorrect impact symbols")
                sys.exit(1)

        # Checking number of column,weights and impacts is same or not
        if nCol != len(weights)+1 or nCol != len(impact)+1:
            print(
                "ERROR : Imbalance in number of columns,imapct and wieghts")
            sys.exit(1)

        if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
            print("ERROR : Output file extension is wrong")
            sys.exit(1)
        if os.path.isfile(sys.argv[4]):
            os.remove(sys.argv[4])
        # print(" No error found\n\n Applying Topsis Algorithm...\n")
        topsis_pipy(temp_dataset, dataset, nCol, weights, impact)


def Normalize(temp_dataset, nCol, weights):
    # normalizing the array
    # print(" Normalizing the DataSet...\n")
    for i in range(1, nCol):
        temp = 0
        for j in range(len(temp_dataset)):
            temp = temp + temp_dataset.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(temp_dataset)):
            temp_dataset.iat[j, i] = (
                temp_dataset.iloc[j, i] / temp)*weights[i-1]
    return temp_dataset


def Calc_Values(temp_dataset, nCol, impact):
    # print(" Calculating Positive and Negative values...\n")
    positive = (temp_dataset.max().values)[1:]
    negative = (temp_dataset.min().values)[1:]
    for i in range(1, nCol):
        if impact[i-1] == '-':
            positive[i-1], negative[i-1] = negative[i-1], positive[i-1]
    return positive, negative


def topsis_pipy(temp_dataset, dataset, nCol, weights, impact):
    # normalizing the array
    temp_dataset = Normalize(temp_dataset, nCol, weights)

    # Calculating positive and negative values
    positive, negative = Calc_Values(temp_dataset, nCol, impact)

    # calculating topsis score
    # print(" Generating Score and Rank...\n")
    score = []
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, nCol):
            temp_p = temp_p + (positive[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (negative[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
    dataset['Topsis Score'] = score

    # calculating the rank according to topsis score
    dataset['Rank'] = (dataset['Topsis Score'].rank(
        method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})

    # Writing the csv
    # print(" Writing Result to CSV...\n")
    dataset.to_csv(sys.argv[4], index=False)
    # print(" Successfully Terminated")


if __name__ == "__main__":
    main()

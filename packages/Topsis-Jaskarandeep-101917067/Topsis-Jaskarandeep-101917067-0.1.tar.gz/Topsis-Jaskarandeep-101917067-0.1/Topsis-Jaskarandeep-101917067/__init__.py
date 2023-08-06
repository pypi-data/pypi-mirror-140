import pandas as pd
import os
import sys

def main():
	
    if len(sys.argv) != 5:
        print("ERROR : NUMBER OF PARAMETERS")
        print("USAGE : python 101917067.py 101917067-data.csv '1,1,3,1,2' '+,+,-,+,+' 101917067-result.csv")
        exit(1)

    elif not os.path.isfile(sys.argv[1]):
        print(f"ERROR : {sys.argv[1]} Don't exist!!")
        exit(1)

    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        print(f"ERROR : {sys.argv[1]} is not csv!!")
        exit(1)

    else:
        dataset, temp_dataset = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[1])
        nCol = len(temp_dataset.columns.values)

        if nCol < 3:
            print("ERROR : Input file have less then 3 columns")
            exit(1)

        for i in range(1, nCol):
            pd.to_numeric(dataset.iloc[:, i], errors='coerce')
            dataset.iloc[:, i].fillna((dataset.iloc[:, i].mean()), inplace=True)

        try:
            weights = [int(i) for i in sys.argv[2].split(',')]
        except:
            print("ERROR : In weights array please check again")
            exit(1)


        impact = sys.argv[3].split(',')
        for i in impact:
            if not (i == '+' or i == '-'):
                print("ERROR : In impact array please check again")
                exit(1)

        if nCol != len(weights)+1 or nCol != len(impact)+1:
            print("ERROR : Number of weights, number of impacts and number of columns not same")
            exit(1)

       	if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
            print("ERROR : Output file extension is wrong")
            exit(1)

        if os.path.isfile(sys.argv[4]):
            os.remove(sys.argv[4])

       	topsis_Jaskarandeep_101917067(temp_dataset, dataset, nCol, weights, impact)


def Normalize(temp_dataset, nCol, weights):
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


def topsis_Jaskarandeep_101917067(temp_dataset, dataset, nCol, weights, impact):
    temp_dataset = Normalize(temp_dataset, nCol, weights)
    positive, negative = Calc_Values(temp_dataset, nCol, impact)

    score = []
    for i in range(len(temp_dataset)):
        temp_pos, temp_neg = 0, 0
        for j in range(1, nCol):
            temp_pos = temp_pos + (positive[j-1] - temp_dataset.iloc[i, j])**2
            temp_neg = temp_neg + (negative[j-1] - temp_dataset.iloc[i, j])**2
        temp_pos, temp_neg = temp_pos**0.5, temp_neg**0.5
        score.append(temp_neg/(temp_pos + temp_neg))
    dataset['Topsis Score'] = score

    dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})

    dataset.to_csv(sys.argv[4], index=False)

if __name__ == "__main__":
    main()

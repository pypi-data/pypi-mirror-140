import pandas as pd
import os
import sys
import logging


def main():
    logging.basicConfig(filename='101903776-log.txt',encoding='utf-8', errors='ignore',level=logging.DEBUG)

    if len(sys.argv) != 5:
        logging.error('command line arguments error. format: python <Name_of_program> '
                      '<dataset>')
        exit(1)


    elif not os.path.isfile(sys.argv[1]):
        logging.error("ERROR : {sys.argv[1]} Doesn't exist!!")
        exit(1)

    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        logging.error("ERROR : {sys.argv[1]} is not in csv format!!")
        exit(1)

    else:

        
        dataset = pd.read_csv(sys.argv[1])
        if dataset.shape[1] != 6:
            raise ValueError('Incorrect number of Columns')
    
        temp_dataset=dataset
        nCol = len(temp_dataset.columns.values)

        if nCol < 3:
            logging.error("ERROR : input file have less then 3 columns")
            exit(1)
        try:
            weights = [int(i) for i in sys.argv[2].split(',')]
 
        except:
            logging.error("ERROR : = weights array error")
            exit(1)
        impact = sys.argv[3].split(',')
        for i in impact:
            if not (i == '+' or i == '-'):
                logging.error("ERROR : = impact array error")
                exit(1)

        if nCol != len(weights)+1 or nCol != len(impact)+1:
            logging.error(
                "ERROR : Number of weights, number of impacts and number of columns not same")
            exit(1)
        if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
            logging.error("ERROR : Output file extension is wrong")
            exit(1)
        if os.path.isfile(sys.argv[4]):
            os.remove(sys.argv[4])
        

        topsis_pipy(temp_dataset, dataset, nCol, weights, impact)


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
    p_sln = (temp_dataset.max().values)[1:]
    n_sln = (temp_dataset.min().values)[1:]
    for i in range(1, nCol):
        if impact[i-1] == '-':
            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
    return p_sln, n_sln


def topsis_pipy(temp_dataset, dataset, nCol, weights, impact):
    temp_dataset = Normalize(temp_dataset, nCol, weights)

    p_sln, n_sln = Calc_Values(temp_dataset, nCol, impact)

    score = []
    for i in range(len(temp_dataset)):
        temp_p, temp_n = 0, 0
        for j in range(1, nCol):
            temp_p = temp_p + (p_sln[j-1] - temp_dataset.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - temp_dataset.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
    dataset['Topsis Score'] = score

    dataset['Rank'] = (dataset['Topsis Score'].rank(
        method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})


    dataset.to_csv(sys.argv[4], index=False)


if __name__ == "__main__":
    main()
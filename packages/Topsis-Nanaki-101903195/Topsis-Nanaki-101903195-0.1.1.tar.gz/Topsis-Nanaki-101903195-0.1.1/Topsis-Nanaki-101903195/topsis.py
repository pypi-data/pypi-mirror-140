# import time
# start=time.time()
import pandas as pd
import numpy as np
import sys
import string

def topsis_cli():
    if len(sys.argv) != 5:
        print('Incorrect number of parameters.')
        sys.exit()

    filename = sys.argv[1]

    try:
        dataframe = pd.read_csv(filename, header=0, index_col=0)
    except FileNotFoundError:
        print("Wrong file or file path")
        exit()

    if len(dataframe.columns) < 3:
        print("Input file must contain three or more columns.")
        exit()

    try:
        dataframe.values.astype(float)
    except ValueError:
        print("Only numeric values allowed.")
        exit()

    (rows, cols) = dataframe.shape
    weights = sys.argv[2]
    weights = list(map(float, weights.split(',')))

    impacts = sys.argv[3]
    impacts = list(map(str, impacts.split(',')))

    if len(weights) != cols:
        print("No of weights is unequal.")
        exit()
    if len(impacts) != cols:
        print("No of impacts is unequal.")
        exit()

    for i in impacts:
        if i != '+' and i != '-':
            print("Impacts should be '+' or '-' only.")
            exit()

    for i in string.punctuation:
        if i != ',':
            if i in weights:
                print("Weights must be separated by Comma(',').")
                exit()
            if i != '+' and i != '-' and i in impacts:
                print("Impacts must be separated by Comma(',').")
                exit()

    a = dataframe.transpose().to_numpy()
    # converting impacts from +/- to 1/0
    encode_impacts = []
    for i in impacts:
        if i == '+':
            encode_impacts.append(1)
        else:
            encode_impacts.append(0)

    impacts = np.array(encode_impacts)
    # normalize weights to 1
    # normalizing weights between 0 and 1
    t = sum(weights)
    for i in range(cols):
        weights[i] /= t

    weights = np.array(weights)

    # step 1
    # Calculate normalized decision matrix
    a = a / np.array(np.linalg.norm(a, axis=1)[:, np.newaxis])

    # step2
    # Calculate the weighted normalized decision matrix
    a = (weights * a.T).T

    # step 3
    # Determine ideal and negative ideal solutions
    ideal_best = np.max(a, axis=1) * impacts + \
                 np.min(a, axis=1) * (1 - impacts)

    ideal_worst = np.max(a, axis=1) * (1 - impacts) + \
                  np.min(a, axis=1) * impacts

    # step 4
    # calculate TOPSIS score/ or n-dimensional euclidean distance
    distance_best = np.linalg.norm(a - ideal_best[:, np.newaxis], axis=0)
    distance_worst = np.linalg.norm(a - ideal_worst[:, np.newaxis], axis=0)

    score = distance_worst / (distance_worst + distance_best)
    b = sorted(score, reverse=True)
    rank = [0] * rows

    for i in range(rows):
        rank[i] = (b.index(score[i]) + 1)

    dataframe['Topsis Score'] = score
    dataframe['Rank'] = rank
    output = pd.DataFrame(dataframe)

    result_name = sys.argv[4]
    output.to_csv(result_name)

    return

if __name__=="__main__":
    topsis_cli()
    # end=time.time()
    # print("The time of execution of above program is :", end-start)
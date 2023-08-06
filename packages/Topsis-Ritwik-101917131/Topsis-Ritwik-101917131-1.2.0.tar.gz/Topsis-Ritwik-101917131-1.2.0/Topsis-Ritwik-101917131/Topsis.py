import pandas as pd
import os
import sys

def topsis():
    # incorrect no. of parameters
    if len(sys.argv) != 5:
        print("ERROR : Incorrect number of parameters")
        exit(1)

    # File Not Found error
    elif os.path.isfile(sys.argv[1])==False:
        print(f"ERROR : {sys.argv[1]} Don't exist!!")
        exit(1)

    # File extension not csv
    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        print(f"ERROR : {sys.argv[1]} is not csv!!")
        exit(1)

    read_file = pd.read_excel(r'C:\Users\Ritwik Khanna\Desktop\Predictive Statistics\Lab Material\Assignment04 - Topsis\101917131-data.xlsx')
    read_file.to_csv(
       r'C:\Users\Ritwik Khanna\Desktop\Predictive Statistics\Lab Material\Assignment04 - Topsis\101917131-data.csv', index=None, header=True)
    dataset = pd.read_csv(
       sys.argv[1])
    cols = len(dataset.columns.values)
    weights = []
    impact = []

   # less then 3 columns in input dataset
    if cols < 3:
            print("ERROR : Input file have less then 3 columns")
            exit(1)

    # Handeling non-numeric value
    for i in range(1, cols):
        pd.to_numeric(dataset.iloc[:, i], errors='coerce')
        dataset.iloc[:, i].fillna(
                (dataset.iloc[:, i].mean()), inplace=True)

    # Handling errors of weighted and impact arrays
    try:
     weights = sys.argv[2].split(',')
    except:
     print("ERROR : Please provide comma-separted weight values")
     exit(1)
    try:
     weights = [float(i) for i in sys.argv[2].split(',')]
    except:
     print("ERROR : Please provide float values as weights")
     exit(1)
    impact = sys.argv[3].split(',')
    for i in impact:
        if not (i == '+' or i == '-'):
            print("ERROR : Please provide values as (+) or (-) in impact")
            exit(1)

    # Checking number of column,weights and impacts is same or not
    if cols != len(weights)+1 or cols != len(impact)+1:
        print("ERROR : Number of weights, number of impacts and number of columns not same")
        exit(1)

    # Checking output file creation errors
    if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
        print("ERROR : Output file extension is wrong")
        exit(1)
    if os.path.isfile(sys.argv[4]):
        os.remove(sys.argv[4])

    temp_dataset = pd.read_csv(sys.argv[1])
    topsis_pipy(temp_dataset, dataset, cols, weights, impact)

def Normalize(temp_dataset, cols, weights):
    total =0
    for ele in range(0, len(weights)):
     total = total + weights[ele]
    for ele in range(0, len(weights)):
     weights[ele]=weights[ele]/total
    for i in range(1, cols):
        temp = 0
        for j in range(len(temp_dataset)):
            temp = temp + temp_dataset.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(temp_dataset)):
            temp_dataset.iat[j, i] = (temp_dataset.iloc[j, i] / temp)*weights[i-1]
    return temp_dataset

def Calculate_Values(temp_dataset, cols, impact):
    ideal_best = (temp_dataset.max().values)[1:]
    ideal_worst = (temp_dataset.min().values)[1:]
    for i in range(1, cols):
        if impact[i-1] == '-':
            ideal_best[i-1], ideal_worst[i-1] = ideal_worst[i-1], ideal_best[i-1]
    return ideal_best, ideal_worst


def topsis_pipy(temp_dataset, dataset, cols, weights, impact):
    # normalizing the array
    temp_dataset = Normalize(temp_dataset, cols, weights)

    # Calculating positive and negative values
    ideal_best, ideal_worst = Calculate_Values(temp_dataset, cols, impact)

    # calculating topsis score
    score = []
    for i in range(len(temp_dataset)):
        pos_dist = 0
        neg_dist = 0
        # calculating euclidean distance from ideal best and ideal worst
        for j in range(1, cols):
            pos_dist = pos_dist + (ideal_best[j-1] - temp_dataset.iloc[i, j])**2
            neg_dist = neg_dist + (ideal_worst[j-1] - temp_dataset.iloc[i, j])**2
        pos_dist = pos_dist**0.5
        neg_dist = neg_dist**0.5
        score.append(neg_dist/(pos_dist + neg_dist))
    dataset['Topsis Score'] = score

    # calculating the rank according to topsis score
    dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
    dataset = dataset.astype({"Rank": int})
    # Writing the csv
    dataset.to_csv(sys.argv[4], index=False)
    # print("TOPSIS successfully applied")

if __name__ == "__main__":
    topsis()

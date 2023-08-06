
import pandas as pd
import math
import sys
import os

# print("------------------------------------------------------------")
# print("Program Execution Started, Program by: Pratham Kapoor 101903270 3COE11")

weights = []
impacts = []
best_values = []
worst_values = []
colnames = []

# Main Function
def main():
    global colnames
    global weights
    global impacts

    if len(sys.argv) != 5:
        # print("Wrong parameter count, please check you've enetered exactly 5 params")
        # print("Usage: python 101903270.py 101903270-data.csv \"Weights\" \"Impacts\" 101903270-result-1/2.csv")
        exit(0)

    input_path = sys.argv[1]
    cur_dir = os.path.dirname(os.path.realpath('__file__'))
    input = os.path.join(cur_dir, input_path)
    # if not os.path.exists(input):



 
    dataframe = pd.read_csv(input)
    # print("------------------------------------------------------------")
    # print("Cleaning Dataframe")
    final_dataframe = dataframe.drop(['Fund Name'], axis=1)
    colnames = list(final_dataframe.columns)
    # removing all unnecessary non integer data from dataframe
    dataframe.apply(lambda x: pd.to_numeric(
        x, errors='coerce').notnull().all())

    # Error Handling as per question
    for i in range(0, len(sys.argv[2])-1, 2):
        if sys.argv[2][i+1] != ',':
            # print("Weights must be comma separated")
            exit(0)

    for i in range(0, len(sys.argv[3])-1, 2):
        if sys.argv[3][i+1] != ',':
            # print("Impacts must be comma separated")
            exit(0)

    for x in list(sys.argv[3].split(',')):
        if (x != '+') and (x != '-'):
            # print("Impacts must be either '+' or '-' and must be comma separated")
            exit(0)

    weights = list(sys.argv[2].split(','))
    weights = [int(i) for i in weights]
    impacts = list(sys.argv[3].split(','))

    if (len(colnames) != 5 or len(weights) != len(colnames) or (len(weights) != len(impacts))):
        # print("Number of Colums !=5 or Number of Weights != Number of Columns or Number of Impacts != Number of Weights")
        exit(0)

    result_path = sys.argv[4]
    # print("------------------------------------------------------------")
    # print("Applying Topsis Algorithm")
    # operations
    # 1. get_normalised_dataset
    # 2. get_weighted_dataset
    # 3. get_ideal_values
    final_dataframe = get_normalised_dataset(final_dataframe)
    final_dataframe = get_weighted_dataset(final_dataframe)
    get_ideal_values(final_dataframe)
    dataframe = topsis_score(final_dataframe, dataframe)
    # give rank
    dataframe['Rank'] = dataframe['Topsis Score'].rank(ascending=False)
    dataframe.to_csv(result_path, index=False)
    # print("------------------------------------------------------------")
    # print("Output Successfully saved to", result_path)
    # print("------------------------------------------------------------")


# Method Functions start from here
def get_normalised_dataset(dataset):
    for column in range(len(colnames)):
        distance = 0
        for i in range(len(dataset)):
            distance += dataset.iloc[i][column] ** 2
        square_root = math.sqrt(distance)
        dataset[colnames[column]] /= square_root
    return dataset


def get_weighted_dataset(dataset):
    for k in range(len(weights)):
        dataset[colnames[k]] *= weights[k]
    return(dataset)


def get_ideal_values(dataset):
    for i in range(len(colnames)):
        if impacts[i] == '+':
            best_values.append(max(dataset[colnames[i]]))
            worst_values.append(min(dataset[colnames[i]]))
        else:
            best_values.append(min(dataset[colnames[i]]))
            worst_values.append(max(dataset[colnames[i]]))


def topsis_score(dataset, dataframe):
    series1, series2 = [], []
    for i in range(len(dataset)):
        distance1 = 0
        distance2 = 0
        for j in range(len(colnames)):
            distance1 += (dataset.iloc[i][j] - best_values[j])**2
            distance2 += (dataset.iloc[i][j] - worst_values[j])**2
        series1.append(math.sqrt(distance1))
        series2.append(math.sqrt(distance2))
    dataframe['Topsis Score'] = pd.Series(
        series2)/(pd.Series(series1) + pd.Series(series2))
    return dataframe


if __name__ == "__main__":
    main()

import sys
import pandas as pd
import re


# handling errors log
def error_message(msg):
    print(msg)
    with open("error.log", "a") as file:
        file.write(f"{msg}\n")


def norm_method(num, denom, weight):
    return (num / denom) * weight


def normalization(data, weight, length):
    # normalizing values of dataset
    for i, n_col in zip(range(0, length), data.columns[1:]):
        # calculating denominator
        denom = (data[n_col].apply(lambda x: x ** 2).sum()) ** 0.5
        data[n_col] = data[n_col].apply(lambda x: norm_method(x, denom, weight[i]))
    return data


def ideal_values(data, impact):
    # max value in all columns saved to list
    ideal_best = data[1:].max()[1:].tolist()
    # min values in all columns saved to list
    ideal_worst = data[1:].min()[1:].tolist()
    # handling the effect of impacts
    for i in range(len(impact)):
        if impact[i] == '-':
            ideal_best[i], ideal_worst[i] = ideal_worst[i], ideal_best[i]

    return ideal_best, ideal_worst


def euclid_method(value, ideal):
    return (value - ideal) ** 2


def euclidean_distance(data, ideal_best, ideal_worst):
    # calculating the euclidean distance of all values
    pos_score = pd.DataFrame()
    neg_score = pd.DataFrame()
    # calculating square of difference of each value from ideal values and storing to new dataframe
    for i, n_col in zip(range(0, len(data)), data.columns[1:-1]):
        pos_score[i] = (data[n_col].apply(lambda x: euclid_method(x, ideal_best[i])))
        neg_score[i] = (data[n_col].apply(lambda x: euclid_method(x, ideal_worst[i])))
    # calculating performance score by adding all row values, taking their square root and applying formula
    score = (neg_score.sum(axis=1) ** 0.5) / (pos_score.sum(axis=1) ** 0.5 + neg_score.sum(axis=1) ** 0.5)
    return score


def topsis_score(data, dataset, weight, impact, length):
    # applying functions on dataframe
    # applying normalization
    data = normalization(data, weight, length)
    # retrieving ideal values
    ideal_best, ideal_worst = ideal_values(data, impact)
    # obtaining performance score
    score = euclidean_distance(data, ideal_best, ideal_worst)
    dataset["Topsis Score"] = score
    return score


def main():
    # check if all arguments are passed into the function
    if len(sys.argv) != 5:
        exit(error_message(
            "[Errno 101]: Incorrect number of arguments passed. The format is - <program.py> <InputDataFile> "
            "<Weights> <Impacts> <ResultFileName>"))

    # check for input data file argument and its format
    try:
        filename = sys.argv[1]
        if not re.search(r'.xlsx', filename):
            exit(error_message("[Errno 103] Incorrect input file format. Use .xlsx file type only."))
    except IndexError:
        exit(error_message("[Errno 102] No input file passed as argument."))

    # check if file exists
    try:
        dataset = pd.read_excel(filename)
    except FileNotFoundError as f:
        exit(error_message(f))

    # check for weights argument and its format
    try:
        weights = sys.argv[2]
        if not re.match(r'[\d,]*$', weights):
            exit(error_message("[Errno 104] Incorrect weights argument format. Unable to parse values."))
        weights = list(map(int, weights.split(",")))
    except IndexError:
        exit(error_message("[Errno 105] No weights passed as argument"))

    # check for impacts argument and its format
    try:
        impacts = sys.argv[3]
        if not re.match(r'[+,-]*$', impacts):
            exit(error_message("[Error 106] Incorrect impacts argument format. Unable to execute."))
        impacts = impacts.split(',')
    except IndexError:
        exit(error_message("[Errno 107] No impacts passed as argument"))

    # check for result file and its format
    try:
        result_file = sys.argv[4]
        if not re.search(r'.csv', result_file):
            exit(error_message("[Errno 108] Incorrect result file format. Use .csv file type only."))
    except IndexError:
        exit(error_message("[Errno 109] No result file name passed as argument."))

    # converting file to csv
    dataset.to_csv("101903573-data.csv", index=None, header=True)
    df = dataset.copy()

    # checking column count
    if len(df.columns) < 3:
        exit(error_message(["[Errno 110] Insufficient columns. Dataset has less than 3 columns"]))

    # handling nan values
    for col in df.columns:
        if df[col].isnull().values.any():
            df[col].fillna(value=df[col].mean(), inplace=True)

    col_length = len(df.columns[1:])

    # column equality check with weights and impacts
    if col_length != len(weights) or col_length != len(impacts):
        exit(error_message("[Errno 111] Columns, weights, impacts do not have equal number of values."))

    # implementing topsis on dataset
    dataset["Topsis Score"] = topsis_score(df, dataset, weights, impacts, col_length)
    dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
    dataset.to_csv(result_file, index=False)
    print(f"Result saved to {result_file}")


if __name__ == "__main__":
    main()

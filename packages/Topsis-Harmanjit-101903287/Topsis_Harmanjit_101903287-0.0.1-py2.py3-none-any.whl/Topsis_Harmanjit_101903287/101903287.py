import pandas as pd
import os
import sys

# Header
name = "Topsis_Harmanjit_101903287"
__version__ = "0.0.1"
__author__ = 'Harmanjit Singh'
__credits__ = 'Thapar Institute of Engineering and Technology'


# Code
def main():
    # Checking for command line arguments
    if len(sys.argv) != 5:
        print("ERROR : NUMBER OF PARAMETERS")
        print("USAGE EXAMPLE : python 101903287.py <input_file.csv> 1,1,1,1 +,+,-,+ <result_file.csv> ")
        exit(1)

    # Checking for input file in directory
    elif not os.path.isfile(sys.argv[1]):
        print(f"ERROR : {sys.argv[1]} Don't exist!!")
        exit(1)

    # Checking for input file formats
    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        print(f"ERROR : {sys.argv[1]} is not csv!")
        exit(1)
    # Checking for output file formats
    elif (".csv" != (os.path.splitext(sys.argv[4]))[1]):
        print("ERROR : Output file extension is wrong")
        exit(1)

    # Function Code
    else:
        df = pd.read_csv(sys.argv[1])
        col = len(df.columns.values)

        # Checking for columns
        if col < 3:
            print("ERROR : Input file have less than 3 columns")
            exit(1)

        # Handling errors of weighted and impact arrays
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

        # Checking number of column,weights and impacts is same or not
        if col != len(weights)+1 or col != len(impact)+1:
            print(
                "ERROR : Number of weights, number of impacts and number of columns not same")
            exit(1)

        # Handeling non-numeric data and filling non-numeric data with mean
        for i in range(1, col):
            pd.to_numeric(df.iloc[:, i], errors='coerce')
            df.iloc[:, i].fillna((df.iloc[:, i].mean()), inplace=True)

        topsis(df, col, weights, impact)


def normalize(df, col, weights):
    ''' normalizing the dataset'''
    for i in range(1, col):
        temp = 0
        for j in range(len(df)):
            temp = temp + df.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(df)):
            # Pandas iat[] method is used to return data in a dataframe at the passed location.
            df.iat[j, i] = (df.iloc[j, i] / temp)*weights[i-1]
    return df


def calculate_values(df, col, impact):
    '''calculating positive and negative values'''
    p = (df.max().values)[1:]
    n = (df.min().values)[1:]
    for i in range(1, col):
        if impact[i-1] == '-':
            p[i-1], n[i-1] = n[i-1], p[i-1]
    return p, n


def topsis(df, col, weights, impact):
    '''calculating topsis score and rank'''

    # normalizing the array
    df = normalize(df, col, weights)

    # Calculating positive and negative values
    p, n = calculate_values(df, col, impact)

    score = []
    for i in range(len(df)):
        temp_p, temp_n = 0, 0
        for j in range(1, col):
            temp_p = temp_p + (p[j-1] - df.iloc[i, j])**2
            temp_n = temp_n + (n[j-1] - df.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
    df['Topsis Score'] = score

    # calculating the rank according to topsis score
    df['Rank'] = (df['Topsis Score'].rank(method='max', ascending=False))
    df = df.astype({"Rank": int})

    # Writing the csv
    # print(" Writing Result to CSV...\n")
    df.to_csv(sys.argv[4], index=False)


if __name__ == "__main__":
    main()

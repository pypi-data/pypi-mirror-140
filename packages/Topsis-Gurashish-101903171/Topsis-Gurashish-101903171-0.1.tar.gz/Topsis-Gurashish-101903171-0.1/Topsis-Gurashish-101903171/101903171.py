import sys
import os.path
import pandas as pd
from pathlib import Path


def Calc_Values(dataset, nCol, impact):
    p_sln = (dataset.max().values)[1:]
    n_sln = (dataset.min().values)[1:]
    for i in range(1, nCol):
        if impact[i-1] == '-':
            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
    return p_sln, n_sln


def Normalize(dataset, nCol, weights):
    for i in range(1, nCol):
        temp = 0
        for j in range(len(dataset)):
            temp = temp + dataset.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(dataset)):
            dataset.iat[j, i] = (dataset.iloc[j, i] / temp)*weights[i-1]
    return dataset


def main():
    if len(sys.argv) != 5:
        print("Incorrect number of arguments")
        sys.exit(0)

    if(os.path.exists(sys.argv[0]) == False):
        print('File does not exist')
        sys.exit(0)

    weights = [int(x) for x in sys.argv[2].split(',')]

    impact = sys.argv[3].split(',')

    df = pd.read_csv(sys.argv[1])
    df_copy = df.copy()
    normailzed_df = Normalize(df_copy, len(df.columns)-1, weights)
    p_sln, n_sln = Calc_Values(
        normailzed_df, len(normailzed_df.columns)-1, impact)

    score = []  # Topsis score
    pp = []  # distance positive
    nn = []  # distance negative

    for i in range(len(normailzed_df)):
        temp_p, temp_n = 0, 0
        for j in range(1, len(normailzed_df.columns)):
            temp_p = temp_p + (p_sln[j-1] - normailzed_df.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - normailzed_df.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
        nn.append(temp_n)
        pp.append(temp_p)

    df['Topsis Score'] = score
    df['Rank'] = (df['Topsis Score'].rank(method='max', ascending=False))
    df = df.astype({"Rank": int})

    output_file = Path(sys.argv[4])
    df.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()

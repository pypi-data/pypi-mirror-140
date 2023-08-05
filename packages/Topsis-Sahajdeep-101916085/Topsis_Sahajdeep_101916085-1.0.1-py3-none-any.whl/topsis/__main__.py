import sys
import pandas as pd
import numpy as np

def main():
    if len(sys.argv)!=5:
        print("Parameter Error")
        exit()

    try:
        with open(sys.argv[1], 'r') as my_file:
            file=pd.read_csv(my_file)
    except FileNotFoundError:
        print("File not found")
        exit()

    df=pd.DataFrame(data=file)

    weights = list(sys.argv[2].split(","))
    impacts = list(sys.argv[3].split(","))
    ncol = len(df.columns)

    punct_dict = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '+': True, '*': True,'-': True, '=': True}
    punct_dict2 = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '*': True, '=': True}

    def char_check(new_list, punct_dict):
        for item in new_list:
            for char in item:
                if char in punct_dict:
                    return False

    def string_check(comma_check_list, punct_dict):
        for string in comma_check_list:
            new_list = string.split(",")
            if char_check(new_list, punct_dict) == False:
                print("Values not comma separated")
                exit()

    string_check(sys.argv[2], punct_dict)
    string_check(sys.argv[3], punct_dict2)

    if ncol<3:
        print("Columns less than 3. Check the data.")
        exit()

    if len(impacts) != (ncol-1):
        print("Problem in number of entered values in impacts. It should be same as number of columns.")
        exit()

    if len(weights) != (ncol-1):
        print("Problem in number of entered values in weights. It should be same as number of columns.")
        exit()

    ls = {'-','+'}
    if set(impacts) != ls:
        print(r"Impacts should be either '+' or '-'.")
        exit()

    for index,row in df.iterrows():
        try:
            float(row['P1'])
            float(row['P2'])
            float(row['P3'])
            float(row['P4'])
            float(row['P5'])
        except:
            df.drop(index,inplace=True)
    df["P1"] = pd.to_numeric(df["P1"], downcast="float")
    df["P2"] = pd.to_numeric(df["P2"], downcast="float")
    df["P3"] = pd.to_numeric(df["P3"], downcast="float")
    df["P4"] = pd.to_numeric(df["P4"], downcast="float")
    df["P5"] = pd.to_numeric(df["P5"], downcast="float")
    df1 = df.copy(deep=True)
    def Normalize(df, nCol, weights):
        for i in range(1, nCol):
            temp = 0
            for j in range(len(df)):
                temp = temp + df.iloc[j, i]**2
            temp = temp**0.5
            for j in range(len(df)):
                df.iat[j, i] = (float(df.iloc[j, i])) / float(temp)*float(weights[i-2])

    def Calc_Values(df, ncol, weights):
        p_sln = (df.max().values)[1:]
        n_sln = (df.min().values)[1:]
        for i in range(1, ncol):
            if impacts[i-2] == '-':
                p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
        return p_sln, n_sln

    Normalize(df,ncol,weights)
    p_sln, n_sln = Calc_Values(df, ncol, impacts)
    score = []
    pp = []
    nn = []

    for i in range(len(df)):
        temp_p, temp_n = 0, 0
        for j in range(1, ncol):
            temp_p = temp_p + (p_sln[j-1] - df.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - df.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append(temp_n/(temp_p + temp_n))
        nn.append(temp_n)
        pp.append(temp_p)

    df1['Topsis Score'] = score
    df1['Rank'] = (df1['Topsis Score'].rank(method='max', ascending=False))
    df1 = df1.astype({"Rank": int})
    df1.to_csv(sys.argv[4],index=False)

if __name__ == '__main__':
    main()

import sys
import pandas as pd
import numpy as np

def main():
    if len(sys.argv)!=5:
        print("Parameter Error")
        exit()
    try:
        with open(sys.argv[1], 'r') as filee:
            file=pd.read_csv(filee)
    except FileNotFoundError:
        print("File not found")
        exit()

    dataframe=pd.DataFrame(data=file)

    wgh = list(sys.argv[2].split(","))
    impct = list(sys.argv[3].split(","))
    ncol = len(dataframe.columns)

    punctuation_dictionary = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '+': True, '*': True,'-': True, '=': True}
    punctuation_dictionary2 = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '*': True, '=': True}

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

    string_check(sys.argv[2], punctuation_dictionary)
    string_check(sys.argv[3], punctuation_dictionary2)

    if ncol<3:
        print("No of columns are less than 3.")
        exit()

    if len(impct) != (ncol-1):
        print("No of values in impacts should be same as the number of columns.")
        exit()

    if len(wgh) != (ncol-1):
        print("No of values in weights should be same as the number of columns.")
        exit()

    lis = {'-','+'}
    if set(impct) != lis:
        print(r"Impacts should be either '+' or '-'.")
        exit()

    for index,row in dataframe.iterrows():
        try:
            float(row['P1'])
            float(row['P2'])
            float(row['P3'])
            float(row['P4'])
            float(row['P5'])
        except:
            dataframe.drop(index,inplace=True)
    dataframe["P1"] = pd.to_numeric(dataframe["P1"], downcast="float")
    dataframe["P2"] = pd.to_numeric(dataframe["P2"], downcast="float")
    dataframe["P3"] = pd.to_numeric(dataframe["P3"], downcast="float")
    dataframe["P4"] = pd.to_numeric(dataframe["P4"], downcast="float")
    dataframe["P5"] = pd.to_numeric(dataframe["P5"], downcast="float")
    dataframe1 = dataframe.copy(deep=True)
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
            if impct[i-2] == '-':
                p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
        return p_sln, n_sln

    Normalize(dataframe,ncol,wgh)
    p_sln, n_sln = Calc_Values(dataframe, ncol, impct)
    score = []
    pp = []
    nn = []

    for i in range(len(dataframe)):
        temp_p, temp_n = 0, 0
        for j in range(1, ncol):
            temp_p = temp_p + (p_sln[j-1] - dataframe.iloc[i, j])**2
            temp_n = temp_n + (n_sln[j-1] - dataframe.iloc[i, j])**2
        temp_p, temp_n = temp_p*0.5, temp_n*0.5
        score.append(temp_n/(temp_p + temp_n))
        nn.append(temp_n)
        pp.append(temp_p)


    dataframe1['Topsis Score'] = score
    dataframe1['Rank'] = (dataframe1['Topsis Score'].rank(method='max', ascending=False))
    dataframe1 = dataframe1.astype({"Rank": int})
    dataframe1.to_csv(sys.argv[4],index=False)

if __name__ == '__main__':
    main()

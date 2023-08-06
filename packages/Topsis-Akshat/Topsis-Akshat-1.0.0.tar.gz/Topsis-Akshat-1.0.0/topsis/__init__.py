
from argparse import ArgumentParser
from pathlib import Path
import pandas as pd
import sys



def topsis(input_file, weight, impacts, resultFileName):

    try:
        # path = Path(input_file)

        # if not path.is_file():
        #     print('File not found!!')
        #     exit()


        df=pd.read_csv(input_file)
        if df.shape[1]<3 :
            print('Input file contains less 3 columns')
            exit()

        # Checking whether dataframe contains only numeric values or not
        check_numeric= df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
        for i in range(1, df.shape[1]):
            if check_numeric[i]!=True :
                print("Non-numerical values found in column no: ", i)
                exit()


        # weight = sys.argv[2]
        # impacts = sys.argv[3]
        # resultFileName = sys.argv[4]


        weight = weight.split(",")
        weights=[]
        for i in range(0, len(weight)):
            weights.append(int(weight[i]))

        impacts = impacts.split(",")

        # Checking size of columns, weights and impacts
        if len(impacts)!= len(weights) or len(impacts)!=(df.shape[1]-1) :
            print("Size of impacts and weights doesn't matches required size of columns in given dataset")
            exit()

        for i in range(0, len(impacts)):
            if impacts[i]!='-' and impacts[i]!='+':
                print("Impacts contains values other than '+' and '-'")
                exit()
        
    except Exception as ex:
        print(ex)
        exit()







    # read_file = pd.read_excel (r'C:\Users\hp\Desktop\Assignment-4\Input files for Assignment04\data.xlsx')
    # df = read_file.to_csv (r'C:\Users\hp\Desktop\Assignment-4\Input files for Assignment04\data.csv', index = None, header=True)
    # read_file

    # df=pd.read_csv(r'C:\Users\hp\Desktop\Assignment-4\Input files for Assignment04\data.csv')
    result=df.copy()
    df

    def normalize(df1, nCol, wt):
        for i in range(1, nCol):
            temp = 0

            for j in range(len(df1)):
                temp = temp + df1.iloc[j, i]**2
            temp = temp**0.5

            for j in range(len(df1)):
                df1.iloc[j, i] = (df1.iloc[j, i] / temp)*wt[i-1]
        # print(df1)

    normalize(df, df.shape[1], weights)
    df

    df.shape

    # ideal best value and ideal worst value
    def idealValues(df2, nCol, impact):
        p_ideal = (df2.max().values)[1:]
        n_ideal = (df2.min().values)[1:]
        for i in range(1, nCol):
            if impact[i-1] == '-':
                p_ideal[i-1], n_ideal[i-1] = n_ideal[i-1], p_ideal[i-1]
        return p_ideal, n_ideal

    # Calculating values
    p_ideal, n_ideal = idealValues(df, df.shape[1], impacts)

    # calculating topsis score
    topsis_score = [] # Topsis score
    p_dist = [] # distance positive
    n_dist = [] # distance negative

    p_ideal

    n_ideal

    # Calculating distances and Topsis score for each row
    for i in range(len(df)):
        temp_p, temp_n = 0, 0
        for j in range(1, df.shape[1]):
            temp_p = temp_p + (p_ideal[j-1] - df.iloc[i, j])**2
            temp_n = temp_n + (n_ideal[j-1] - df.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        topsis_score.append(temp_n/(temp_p + temp_n))
        n_dist.append(temp_n)
        p_dist.append(temp_p)

    n_dist

    p_dist

    topsis_score

    # append topsis score to the dataset   
    result['Topsis Score'] = topsis_score

    # calculate rank according to the topsis score
    result['Rank'] = (result['Topsis Score'].rank(method='max', ascending=False))
    result = result.astype({"Rank": int})

    print(result)


    # result.info()

    result.to_csv(resultFileName, index=False)
    print("Result stores in file :", resultFileName)
    df
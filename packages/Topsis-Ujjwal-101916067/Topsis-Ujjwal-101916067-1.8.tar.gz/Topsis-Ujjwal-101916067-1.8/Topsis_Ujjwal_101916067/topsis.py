import pandas  as pd
import copy as copy
import numpy as np
import sys
import os
import logging

logging.basicConfig(filename='101916067-1.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

class Error(Exception): # Base class for other exceptions
    pass

class WrongArgumentsNumber(Error): # Raised when number of arguments are more than two
    pass

class NotAdequateColumns(Error): # Raised when number of columns in input file are not 3
    pass

class WrongOutputFileName(Error):
    pass

class WrongInputFileName(Error):
    pass

class NotAdequateInput(Error):
    pass

class WrongImpactArguments(Error):
    pass



def ujjwal_topsis(df, weight, impact):
    initial_df = df
    # Converting to floats - handling non-numeric values
    col = df.columns

    for i in range(1,len(col)):
        df[col[i]] = pd.to_numeric(df[col[i]], downcast="float")

    for i in range(len(weight)):
        weight[i] = float(weight[i])


    # Normalisation
    squares = []
    for i in df.columns[1:]:
        temp = 0
        for j in range(len(df.index)):
            temp += np.square(float(df.iloc[j][i]))
        squares.append(temp)

    # print(squares)
    k=0
    df_li = []
    for i in df.columns[1:]:
        # print(i)
        li = []
        for j in range(len(df.index)):
            a = float(df.iloc[j][i] / np.sqrt(squares[k]))
            li.append(a)

        df_li.append(li)
        k+=1

    new_df = pd.DataFrame()
    new_df[df.columns[0]] = df[df.columns[0]]


    for i in range(len(df_li)):
        new_df[df.columns[i+1]] = df_li[i]

    df = new_df


    # Multiplying with weights
    df_li = []
    k=0
    for i in df.columns[1:]:
        li = []
        for j in range(len(df.index)):
            a = df.iloc[j][i] * (weight[k])
            # df.iloc[j][i] = a
            li.append(a)
        df_li.append(li)
        k+=1

    new_df = pd.DataFrame()
    new_df[df.columns[0]] = df[df.columns[0]]

    for i in range(len(df_li)):
        new_df[df.columns[i+1]] = df_li[i]

    df = new_df

    # STEP 4 - Find ideal best and ideal worst 
    maximum = ['Ideal Best']
    minimum = ['Ideal Worst']

    for i in df.columns[1:]:
        column = df[i]
        max_value = column.max()
        maximum.append(max_value)
        min_value = column.min()
        minimum.append(min_value)

    k=1
    for i in impact:
        if i=='-':
            temp = maximum[k]
            maximum[k] = minimum[k]
            minimum[k] = temp
        k+=1
          
    df.loc[len(df.index)] = maximum
    df.loc[len(df.index)] = minimum

    # print(maximum)
    # print(minimum)

    # STEP 5 - Row wise Eucledian
    s_max = []
    s_min = []

    for j in range(len(df.index) - 2):
        temp_max = 0
        temp_min = 0
        for i in df.columns[1:]:
            temp_max += np.square(df.iloc[j][i] - df.iloc[-2][i])
            temp_min += np.square(df.iloc[j][i] - df.iloc[-1][i])

        s_max.append(round(np.sqrt(temp_max),4))
        s_min.append(round(np.sqrt(temp_min),4))

    df = df.iloc[:-2 , :] # Removing the last two rows
    
    avg_s = []
    for i in range(len(s_max)):
        avg_s.append((s_max[i] + s_min[i]))

    # print('S_max: ', s_max)
    # print('S_min: ', s_min)
    # print('Avg s: ', avg_s)

    # STEP 6 - Finding performance
    per = []
    for i in range(len(s_min)):
        per.append((s_min[i]/avg_s[i]))


    df = df.assign(Topsis_Score = per)
    df['Rank'] = df['Topsis_Score'].rank(ascending = 0)

    ranking = []
    for m in range(len(df.index)):
        ranking.append(int(df.loc[m]['Rank']))
            
    df.drop(['Rank'], axis = 1)

    df['Rank'] = ranking

    initial_df['Topsis Score'] = df['Topsis_Score']
    initial_df['Rank'] = df['Rank']

    # print(df)
    return initial_df



n = len(sys.argv)

try:
    if n!=5:
        raise WrongArgumentsNumber
    else:
        inFile = sys.argv[1]
        weight = sys.argv[2]
        impact = sys.argv[3]
        result_file = sys.argv[4]
        # df = pd.read_excel('data.xlsx')
        # df.to_csv (inFile, index = None, header=True)
        df = pd.read_csv(inFile)

    # if inFile[-18:]!='101916067-data.csv':
    #     raise WrongInputFileName

    if not os.path.exists(sys.argv[1]):
        raise FileNotFoundError

    # if result_file[-20:]!='101916067-result.csv':
    #     raise WrongOutputFileName

    if len(df.columns)<3:
        raise NotAdequateColumns

    impact_li = impact.split(',')
    # This also checks impacts separated by commas as this is splitted by ',' and if something else eill come, the list would not match
    for i in impact_li: 
        if i!='-' and i!='+':
            raise WrongImpactArguments

    try:
        weight_li = weight.split(',')
        weights=[float(i) for i in sys.argv[2].split(',')]
    except:
        print("Weights not separated by commas")
        logging.error("Weights shiuld be separated by commas")

    if len(weight_li)!=len(impact_li):
        raise NotAdequateInput
    elif len(weight_li)!=len(df.columns[1:]):
        raise NotAdequateInput


    ans_df = ujjwal_topsis(df, weight_li, impact_li)
    ans_df.to_csv(result_file, index = False)


except WrongArgumentsNumber:
    print("Enter 5 arguments.")
    logging.error('Give 5 arguments')
    
except FileNotFoundError:
    print("Input file not found")
    logging.error('File not Found')

except WrongOutputFileName:
    print("The name of the output file is wrong.")
    logging.error("Wrong name of output file")

except WrongInputFileName:
    print("The name of the input file is wrong.")
    logging.error("Wrong name of input file") 

except NotAdequateColumns:
    print("Columns in input file are not equal to 3")
    logging.error("Columns in input file are not equal to 3")

except NotAdequateInput:
    print("Enter the correct input.")
    logging.error("Wrong Input")

except WrongImpactArguments:
    print("Enter correct impact arguments.")
    logging.error("Wrong Impact Arguments") 







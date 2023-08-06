import sys
import logging
import pandas as pd
import math
logging.basicConfig(filename="101917115-log.txt",
                    format='%(asctime)s %(message)s', filemode='w')


def main():
    InputDataFile = sys.argv[1]
    Weights = sys.argv[2]
    Impacts = sys.argv[3]
    ResultFileName = sys.argv[4]

    try:
        input = pd.read_csv(InputDataFile)

        if(len(input.columns) < 3):
            logging.error('Input file must contain three or more columns')
            exit()
        weights = [float(i) for i in Weights.split(",")]
        if(len(weights) != len(input.columns)-1):
            logging.error(
                'Number of weights and number of columns(from 2nd to last columns) must be same.')
            exit()
        impact = Impacts.split(",")
        if(len(impact) != len(input.columns)-1):
            logging.error(
                'Number of impact and number of columns(from 2nd to last columns) must be same')
            exit()

        for i in impact:
            if(i != '+' and i != '-'):
                logging.error('Impacts must be either +ve or -ve')
                exit()

    except Exception as error:
        logging.exception(error)
        exit()

    df = input.drop(['Fund Name'], axis=1)
    for i in df.columns:
        s = (df[i]**2).sum()
        s = math.sqrt(s)
        df[i] = df[i].div(s)

    weights = [float(i) for i in Weights.split(",")]

    for i in range(len(df)):
        for j in range(len(df.columns)):
            df.iat[i, j] = (df.iloc[i, j])*weights[j]

    vp = []
    vn = []
    k = 0
    for i in df.columns:
        if(impact[k] == "+"):
            vp.append(df[i].max())
            vn.append(df[i].min())
        else:
            vp.append(df[i].min())
            vn.append(df[i].max())
        k = k+1

    score = []
    for i in range(len(df)):
        p=0
        n=0 
        for j in range(len(df.columns)):
            a = vp[j] - df.iloc[i, j]
            a = a**2
            p = p + a
            
            b = vn[j] - df.iloc[i, j]
            b = b**2
            n = n + b
            
        p = p**0.5
        n = n**0.5
        score.append(n/(p + n))


    df['Topsis Score'] = score
    df['Rank'] = (df['Topsis Score'].rank(method='max', ascending=False))
    df = df.astype({"Rank": int})
    
    df.to_csv(ResultFileName)


if __name__ == "__main__":
    if(len(sys.argv) > 5):
        logging.error('Number of inputed arguments are more than five')
    elif(len(sys.argv) < 5):
        logging.error('Number of inputed arguments are less than five')
    else:
        main()

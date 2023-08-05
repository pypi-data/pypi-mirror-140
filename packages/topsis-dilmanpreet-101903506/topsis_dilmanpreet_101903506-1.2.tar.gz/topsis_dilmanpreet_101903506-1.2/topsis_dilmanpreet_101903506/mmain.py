import pandas as pd
import os
import sys


def main(): 
    
    if len(sys.argv) != 5:
        print("ERROR : Incorrect number of parameters")
        print("Use Correct Input Format: python topsis.py inputfile.csv '1,1,1,1,2' '+,+,-,+,-' result.csv")
        sys.exit()

    elif not os.path.isfile(sys.argv[1]):
        print("ERROR :" ,sys.argv[1], "File Doesn't exist")
        sys.exit()

    else:
        try: 
            df, temp_df = pd.read_csv(
            sys.argv[1]), pd.read_csv(sys.argv[1])
            numberOfCol = len(temp_df.columns.values)
        except:
            print("ERROR :",sys.argv[1], "incorrect file format")
            sys.exit()

        
        if numberOfCol < 3:
            print("ERROR : Input file have less then 3 columns")
            sys.exit()
    count=0
    for k in range(1,numberOfCol):
        for j in range(df.shape[0]):
            try:
                #print(count)
                count+=1
                xd = float(df.iloc[j,k])
            except:
                print("ERROR: Only numerical values are accepted")
                sys.exit()
        

    try:
        weights = [int(i) for i in sys.argv[2].split(',')]
    except:
        print("ERROR : Check weights array and retry")
        sys.exit()
    impact = sys.argv[3].split(',')
    for i in impact:
        if not (i == '+' or i == '-'):
            print("ERROR : Check Impact array and retry")
            sys.exit()

    
    if numberOfCol != len(weights)+1 or numberOfCol != len(impact)+1:
        print(
            "ERROR : Number of weights, impacts and columns are not the same")
        sys.exit()

    if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
        print("ERROR : Output file extension is wrong")
        sys.exit()
    if os.path.isfile(sys.argv[4]):
        os.remove(sys.argv[4])
    
    topsis_pipy(temp_df, df, numberOfCol, weights, impact)


def Normalize(temp_df, numberOfCol, weights):        
    for i in range(1, numberOfCol):
        temp = 0
        for j in range(len(temp_df)):
            temp = temp + temp_df.iloc[j, i]**2
        temp = temp**0.5
        for j in range(len(temp_df)):
            temp_df.iat[j, i] = (
                temp_df.iloc[j, i] / temp)*weights[i-1]
    return temp_df


def Calcn(temp_df, numberOfCol, impact):
    posit = (temp_df.max().values)[1:]
    negit = (temp_df.min().values)[1:]
    for i in range(1, numberOfCol):
        if impact[i-1] == '-':
            posit[i-1], negit[i-1] = negit[i-1], posit[i-1]
    return posit, negit


def topsis_pipy(temp_df, df, numberOfCol, weights, impact):
    temp_df = Normalize(temp_df, numberOfCol, weights)
    posit, negit = Calcn(temp_df, numberOfCol, impact)

    score = []
    for i in range(len(temp_df)):
        temp_p, temp_n = 0, 0
        for j in range(1, numberOfCol):
            temp_p = temp_p + (posit[j-1] - temp_df.iloc[i, j])**2
            temp_n = temp_n + (negit[j-1] - temp_df.iloc[i, j])**2
        temp_p, temp_n = temp_p**0.5, temp_n**0.5
        score.append((temp_n/(temp_p + temp_n))*100)

    df['Topsis Score'] = score

    
    df['Rank'] = (df['Topsis Score'].rank(
        method='max', ascending=False))
    df = df.astype({"Rank": int})
    
    df.to_csv(sys.argv[4], index=False)

if __name__ == "__main__":
    main()
    

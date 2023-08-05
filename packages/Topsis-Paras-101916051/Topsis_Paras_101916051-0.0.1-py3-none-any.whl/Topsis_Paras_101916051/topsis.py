import pandas as pd
import numpy as np
import os,sys

def solve(df,weights,impact):
    # Normalization
    j=0
    for col in df.columns[1:]:
        df[col]=(df[col]/np.sqrt(np.square(df[col]).sum()))*weights[j]
        j+=1
    
    # Calculating score
    pos_dist=df.max().values[1:]
    neg_dist=df.min().values[1:]
    score=[]
    for i in range(len(df)): # Traversing each row
        j=0
        pos_val=0
        neg_val=0
        for col in df.columns[1:]: # Traversing each col
            pdist=pos_dist[j]
            ndist=neg_dist[j]
            if impact[j]=='-':
                pdist,ndist=ndist,pdist
            pos_val+=np.square(df.iloc[i][col]-pdist)
            neg_val+=np.square(df.iloc[i][col]-ndist)
            j+=1
        pos_val=np.sqrt(pos_val)
        neg_val=np.sqrt(neg_val)
        score.append(neg_val/(pos_val+neg_val))
    df['Score']=score

    # Calculating Rank
    df['Rank']=df['Score'].rank(method='max',ascending=False)
    df = df.astype({"Rank": int})

    # Writing result to csv
    df.to_csv(sys.argv[4], index=False)

def main():
    if len(sys.argv)!=5:
        print("ERROR : NUMBER OF PARAMETERS")
        print("USAGE : python topsis.py inputfile.csv '1,1,1,1' '+,+,-,+' result.csv ")
        exit(1)
    elif not os.path.isfile(sys.argv[1]):
        print(f"""ERROR : File "{sys.argv[1]}" not found!!""")
        exit(1)
    elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        print(f"ERROR : {sys.argv[1]} is not csv file!!")
        exit(1)
    try:
        file_path=os.getcwd() + "\\" + sys.argv[1]
        with open(file_path):
            df=pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"""ERROR : File "{sys.argv[1]}" not found!!""")
        exit(1)
    if len(df.columns)<3:
        print("ERROR: Input file should contain more than 2 columns!")
        exit(1)

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
    if len(df.columns)-1 != len(weights) or len(df.columns)-1 != len(impact):
        print("ERROR : Number of weights, number of impacts and number of columns not same")
        exit(1)

    if (".csv" != (os.path.splitext(sys.argv[4]))[1]):
        print("ERROR : Output file extension is wrong")
        exit(1)
    if os.path.isfile(sys.argv[4]):
        os.remove(sys.argv[4])
    # Handeling non-numeric value
    for i in range(1, len(df.columns)):
        pd.to_numeric(df.iloc[:, i], errors='coerce')
        df.iloc[:, i].fillna((df.iloc[:, i].mean()), inplace=True)
    solve(df,weights,impact)

if __name__=="__main__":
    main()
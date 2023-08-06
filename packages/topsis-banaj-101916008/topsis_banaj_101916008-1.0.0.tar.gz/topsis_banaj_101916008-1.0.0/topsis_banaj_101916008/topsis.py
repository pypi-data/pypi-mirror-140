#
#   Banaj
#   101916008
#   Thapar University, Patiala
#
import os
import sys
import pandas as pd

def main():
    
    if len(sys.argv) != 5:
        print("Error : Insufficient number of parameters provided! Can only accept 5.")
        exit(1)
    
    if not os.path.isfile(sys.argv[1]):
        print("Error : File doesn't exists!")
        exit(1)
    
    fname = sys.argv[1]
    df = pd.read_csv(fname)
    
    if len(df.columns) < 3:
        print("Error : Input file must contain 3 or more columns.")
        exit(1)
        
    for i in range(1, len(df.columns)):
        pd.to_numeric(df.iloc[:, i], errors='coerce')
        df.iloc[:, i].fillna(df.iloc[:, i].median(), inplace=True)
        
    try:
        weights = [int(i) for i in sys.argv[2].split(',')]
    except:
        print("Error : Incorrect weight format!")
        exit(1)
        
    impacts = sys.argv[3].split(',')
    for i in impacts:
        if not (i == '+' or i == '-'):
            print("Error : Incorrect Impacts format!")
            exit(1)
            
    if len(df.columns) != len(weights) + 1 or len(df.columns) != len(impacts) + 1:
        print("Error : Number of weights / impacts and number of columns do not match!")
        exit(1)
    
    if (".csv" != os.path.splitext(sys.argv[4])[1]):
        print("Error : Incorrect format of output file!")
        exit(1)
    
    def normalize(df, weight):
        
        for j in range(1, len(df.columns)):
            
            rms = 0
            for i in range(len(df)):
                rms += df.iloc[i,j]**2
            
            rms = rms**0.5
            
            for i in range(len(df)):
                df.iat[i, j] = (df.iloc[i,j] / rms) * weight[j-1]
                
        return df
    
    def idealValues(df, impacts):
        idealBest = df.max().values[1:] # for each column
        idealWorst = df.min().values[1:]
        
        for i in range(1, len(df.columns)):
            if impacts[i-1] == '-':
                idealBest[i-1], idealWorst[i-1] = idealWorst[i-1], idealBest[i-1]
                
        return idealBest, idealWorst
    
    def euclidean(df, idealBest, idealWorst):
        s_pos = []
        s_neg = []
        
        for i in range(len(df)):
            pos = 0
            neg = 0
            for j in range(1, len(df.columns)):
                pos += (idealBest[j-1] - df.iloc[i,j])**2
                neg += (idealWorst[j-1] - df.iloc[i,j])**2
            
            pos = pos**0.5
            neg = neg**0.5
            
            s_pos.append(pos)
            s_neg.append(neg)
            
        return s_pos, s_neg
    
    
    def topsisFunc(df, weights, impacts):
        
        df = normalize(df, weights)
        idealBest, idealWorst = idealValues(df, impacts)
        s_pos, s_neg = euclidean(df, idealBest, idealWorst)
        
        score = []
        
        for i in range(len(s_pos)):
            score.append(s_neg[i] / (s_pos[i] + s_neg[i]))
            
        return score
    
    
    
    #print("Processing...\n")
    dff = df.copy()
    # weights = [1,1,1,1,1]
    # impacts = ['+', '+', '-', '+', '+']
    
    score = topsisFunc(dff, weights, impacts)
    df['Topsis Score'] = score
    
    df['Rank'] = df['Topsis Score'].rank(method='max', ascending=False)
    df = df.astype({"Rank" : int})
    
    df.to_csv('101916008-result.csv', index=False)
    
    #print("Done.")

if __name__ == "__main__":
    main()
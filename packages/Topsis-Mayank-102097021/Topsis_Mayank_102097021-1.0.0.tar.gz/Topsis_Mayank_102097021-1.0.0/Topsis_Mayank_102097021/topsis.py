import os
import sys
import pandas as pd

def main():
    
    if len(sys.argv) != 5:
        sys.exit("Error : Enter correct number of parameters.\n example : python topsis.py inputfile.csv 1,1,1,1 +,+,-,+ result.csv")
    
    if not os.path.isfile(sys.argv[1]):
        sys.exit("Error : File doesn't exists!")
    
    if ".csv" != (os.path.splitext(sys.argv[1]))[1]:
        sys.exit("Error : Extension of output file must be .csv.")
    
    df = pd.read_csv(sys.argv[1])
    
    if len(df.columns) < 3:
        sys.exit("Error : Input file must contain 3 or more columns.")
        
    for i in range(1, len(df.columns)):
        pd.to_numeric(df.iloc[:, i], errors='coerce')
        df.iloc[:, i].fillna(df.iloc[:, i].mean(), inplace=True)

    try:    
        weights = [int(i) for i in sys.argv[2].split(',')]
    except:
        print("Error : Incorrect weights format!")  
    
    impacts = sys.argv[3].split(',')

    for i in impacts:
        if not (i == '+' or i == '-'):
            sys.exit("Error : Incorrect impacts format!")

    if len(df.columns) != len(weights) + 1 or len(df.columns) != len(impacts) + 1:
        sys.exit("Error : Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.")

    if (".csv" != os.path.splitext(sys.argv[4])[1]):
        sys.exit("Error : Extension of output file must be .csv.")
    
    def normalize(df, weights):   
        for j in range(1, len(df.columns)):
            temp = 0
            for i in range(len(df)):
                temp += df.iloc[i,j]**2
            temp = temp**0.5
            for i in range(len(df)):
                df.iloc[i,j] = (df.iloc[i,j] / temp) * weights[j-1]

        return df
    
    def idealValues(df, impacts):
        idealBest = df.max().values[1:]
        idealWorst = df.min().values[1:]        
        for i in range(1, len(df.columns)):
            if impacts[i-1] == '-':
                idealBest[i-1], idealWorst[i-1] = idealWorst[i-1], idealBest[i-1]
                
        return idealBest, idealWorst
    
    def euclidean_dist(df, idealBest, idealWorst):
        dist_pos = []
        dist_neg = []       
        for i in range(len(df)):
            pos = 0
            neg = 0
            for j in range(1, len(df.columns)):
                pos += (idealBest[j-1] - df.iloc[i,j])**2
                neg += (idealWorst[j-1] - df.iloc[i,j])**2            
            dist_pos.append(pos**0.5)
            dist_neg.append(neg**0.5)
            
        return dist_pos, dist_neg
    
    
    def topsis(df, weights, impacts):  
        df = normalize(df, weights)
        idealBest, idealWorst = idealValues(df, impacts)
        dist_pos, dist_neg = euclidean_dist(df, idealBest, idealWorst)
        
        score = []
        
        for i in range(len(dist_pos)):
            score.append(dist_neg[i] / (dist_pos[i] + dist_neg[i]))
            
        return score
    
    
    df1 = df.copy()   
    score = topsis(df1, weights, impacts)
    df['Topsis Score'] = score
    df['Rank'] = df['Topsis Score'].rank(method='max', ascending=False)
    df = df.astype({"Rank" : int})
    df.to_csv(sys.argv[4], index=False)
    

if __name__ == "__main__":
    main()
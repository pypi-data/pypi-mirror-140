import sys
import numpy as np
import pandas as pd

df = pd.read_csv(r"C:\Users\PRAVEEN\OneDrive\Desktop\Topsis-Manah-102083035-1.0.0\Topsis-Manah-102083035\__init__.py")

def Normalization(df, weights):
    for i in range(df.shape[1]):
        total_sq_sum = 0
        for j in list(df.iloc[:,i]):
            total_sq_sum += j**2
        deno = total_sq_sum**0.5
        
        for ind,k in enumerate(list(df.iloc[:,i])):
            df.iloc[ind,i] = k*weights[i]/deno

def idealBestWorst(df,choose):
    ideal_best = []
    ideal_worst = []
    
    for i in range(df.shape[1]):
        if choose[i] == '+':
            ideal_best.append(df.max()[i])
            ideal_worst.append(df.min()[i])
        else:
            ideal_best.append(df.min()[i])
            ideal_worst.append(df.max()[i])
            
    return ideal_best,ideal_worst

def topsis():
    n = len(sys.argv)
    if n==5:
            inputFileName, weights, impacts, resultFileName = sys.argv[1:]
            weights = [int(w) for w in weights.split(',')]
            impacts = [i for i in impacts.split(',')]

            dataset = pd.read_csv(inputFileName)

            #checking for numeric columns in dataset
            dataset_dtypes = dataset.dtypes.tolist()
            numeric_dtypes = ['int32', 'int64', 'float32', 'float64']
            numeric = []

            for index, i in enumerate(dataset_dtypes):
                if i in numeric_dtypes:
                    numeric.append(index)

            col_list = dataset.columns.tolist()
            numeric_col = [col_list[i] for i in numeric]

            #copy of dataset with only numeric columns 
            df = dataset.loc[:, dataset.columns.isin(numeric_col)].copy()

            if(len(df.columns.tolist())<=1):
                raise Exception("Columns insufficient to calculate topsis!")

            #checking weights, impacts and numeric cols length 
            weights_length = len(weights)
            impacts_length = len(impacts)
            df_cols_length = len(df.columns.tolist())

            if weights_length!=impacts_length or impacts_length!=df_cols_length or df_cols_length!=weights_length:
                raise Exception("Please check the length of Weights, impacts and dataset columns length!")

            for i in impacts:
                if i not in '+ -'.split():
                    raise Exception("Impacts can be only + or -")

            #Normalization
            Normalization(df, weights)

            #calculating best and worst deal
            best, worst = idealBestWorst(df, impacts)

            #calculating topsis score
            dist_pos = []
            dist_neg = []
            for i in range(df.shape[0]):
                    dist_pos.append(np.linalg.norm(df.iloc[i,:].values-best))
                    dist_neg.append(np.linalg.norm(df.iloc[i,:].values-worst))

            score = []
            for i in range(len(dist_pos)):
                score.append(dist_neg[i]/(dist_pos[i]+dist_neg[i]))

            dataset['Topsis Score'] = score
            dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
            dataset = dataset.astype({"Rank": int})

            dataset.to_csv("102083035-result.csv")

    else:
        print("Please check the arguments entered")
        

if __name__ == '__main__':
    topsis()

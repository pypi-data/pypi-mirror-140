import sys
import pandas as pd
import numpy as np
import os

class myexception(Exception):
      pass

def normalised_mat(filename,weights,impact):

    dataset = pd.read_csv(filename)
    column_values = dataset.iloc[:,1:].values
    
    if (dataset.shape[1]<3):
        raise myexception("Input file must contain three or more columns")

    if (len(weights)!=len(impact)!=len(column_values[0][:])):
        raise myexception("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same")

    is_int = dataset.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())
    for i in range(1,len(is_int)):
        if is_int[i]!=True:
            raise myexception("For the Given Dataset from column2 all values must be numeric")


    sum_columns = np.zeros(len(column_values[0]),dtype=float)

    for i in range (len(column_values)):
        for j in range (len(column_values[i])):
            sum_columns[j] += np.square(column_values[i][j])

    for i in range(len(sum_columns)):
        sum_columns[i]=np.sqrt(sum_columns[i]) 

    for i in range(len(column_values)):
        for j in range(len(column_values[i])):
            column_values[i][j]=column_values[i][j]/sum_columns[j]

    return (column_values)


def weight_assign(column_values,weights):
    weights=weights.split(',')
    sum_weights = 0

    sum_weights = sum(map(float,weights))

    for i in range(len(weights)):
        weights[i]=float(weights[i])/sum_weights

    weighted_column_values=[]
    for i in range(len(column_values)):
        temp=[]
        for j in range(len(column_values[i])):
            temp.append(column_values[i][j]*weights[j])
        weighted_column_values.append(temp)

    return(weighted_column_values)    


def performance_score(weighted_column,impacts):
    q =weighted_column
    q = np.array(q)
    q[:,0]

    Vjpositive=np.zeros(len(weighted_column[0]),dtype=float)
    Vjnegative=np.zeros(len(weighted_column[0]),dtype=float)

    for i in range(len(weighted_column[0])):
            if impacts[i]=='+':
                Vjpositive[i]=max(q[:,i])
                Vjnegative[i]=min(q[:,i])
            elif impacts[i]=='-':
                Vjpositive[i]=min(q[:,i])
                Vjnegative[i]=max(q[:,i])

    Sjpositive=np.zeros(len(weighted_column),dtype=float)
    Sjnegative=np.zeros(len(weighted_column),dtype=float)

    for i in range(len(weighted_column)):
        for j in range(len(weighted_column[i])):
            Sjpositive[i]+=np.square(weighted_column[i][j]-Vjpositive[j])
            Sjnegative[i]+=np.square(weighted_column[i][j]-Vjnegative[j])
    for i in range(len(Sjpositive)):
        Sjpositive[i]=np.sqrt(Sjpositive[i])
        Sjnegative[i]=np.sqrt(Sjnegative[i])
    Performance_score=[0]*len(weighted_column)
    for i in range(len(weighted_column)):
        Performance_score[i]=Sjnegative[i]/(Sjnegative[i]+Sjpositive[i])
    
    return(Performance_score)

def adding_data(score,filename):
    df = pd.read_csv(filename)
    df = df.assign(Topsis_Score=score)
    df['Rank'] = df['Topsis_Score'].rank(method='max',ascending=False)
    return (df)

def main():
    if len(sys.argv)!=5:
        raise myexception("You have missed an input file..,Use : python topsis.py inputfile.csv “1,1,1,2” “+,+,-,+” result.csv")

    path=os.getcwd()
    filename = os.path.join(path,sys.argv[1])

    if not os.path.exists(filename):
        raise myexception("file does not exists")

    
    weights = sys.argv[2]
    impacts = sys.argv[3]
    result = sys.argv[4]

    impacts=impacts.split(',')

    for i in range(0,len(impacts)):
        if impacts[i]=='-':
            continue
        elif impacts[i]=='+':
            continue
        else:
            raise myexception("Impacts must be either +ve or -ve.")

    data_table = normalised_mat(filename,weights,impacts)   # normalised the matrix
    wt_given = weight_assign(data_table,weights)            # mutiply each value with their respective weights
    Performance = performance_score(wt_given,impacts)       # calculating performace score for given weight and impact
    new_dataset = adding_data(Performance,filename)         # now adding performace_score and rank to the csv 
    new_dataset.to_csv(result) 

if __name__=='__main__':
    main()
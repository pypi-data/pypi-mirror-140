import sys
import pandas as pd
import math


weights = []
impacts = []
ideal_best = []
ideal_worst = []
column_names = []


def vector_normalise(dataset):
    
    for col in range(len(column_names)):
        distance = 0
        for i in range(len(dataset)):
            distance += dataset.iloc[i][col] ** 2
        sq_root = math.sqrt(distance)
        dataset[column_names[col]] /= sq_root
    return dataset


def weighted_matrix(dataset):
    for k in range(len(weights)):
        dataset[column_names[k]] *= weights[k]
    return(dataset)


def ideal_values(dataset):

    for i in range(len(column_names)):
        if impacts[i] == '+':
            ideal_best.append(max(dataset[column_names[i]]))
            ideal_worst.append(min(dataset[column_names[i]]))
        else:
            ideal_best.append(min(dataset[column_names[i]]))
            ideal_worst.append(max(dataset[column_names[i]]))


def performance_score(dataset, original_db):

    s1, s2 = [], []
    for i in range(len(dataset)):
        d1 = 0
        d2 = 0
        for j in range(len(column_names)):
            d1 += (dataset.iloc[i][j] - ideal_best[j])**2
            d2 += (dataset.iloc[i][j] - ideal_worst[j])**2
        s1.append(math.sqrt(d1))
        s2.append(math.sqrt(d2))
    original_db['Topsis Score'] = pd.Series(s2)/(pd.Series(s1) + pd.Series(s2))
    return original_db


def main():
    if len(sys.argv) != 5:
        print("Incorrect Number of Parameters")
        print("format: python topsis.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        exit(0)



    if len(sys.argv) != 5:
        print("Wrong number of parameters.")
        print("5 parameters are required.")
        print("format: python topsis.py <InputDataFile> <Weights> <Impacts> <ResultFileName>")
        print("example: python topsis.py inputfile.csv “1,1,1,2” “+,+,-,+” result.csv ")
        exit(0)

   
    file_name = sys.argv[1]
    try : 
        df = pd.read_csv(file_name)
    except:
        print("File Not Found")
    df1 = df.drop(['Fund Name'], axis=1)
    column_names = list(df1.columns)
    if len(df.columns) < 3:
        print("The number of columns in the input dataset do not meet the requirements!")
    else:
        colList = df.apply(lambda x: pd.to_numeric(x, errors='coerce').notnull().all())
        for i in range(1,len(column_names)):
            if colList[i]:
                pass
            else:
                print("Error!! %s column contains non-numeric values"%column_names[i-1])

    for i in range(0,len(sys.argv[2])-1,2):
        if sys.argv[2][i+1] != ',':
            print("Weights are not separated by ','.")

    for i in range(0,len(sys.argv[3])-1,2):
        if sys.argv[3][i+1] != ',':
            print("Impacts are not separated by ','.")

    weights = list(sys.argv[2].split(','))
    weights = [int(i) for i in weights]
    impacts = list(sys.argv[3].split(','))
    if (len(weights) != len(column_names)) or (len(impacts) != len(column_names) or (len(weights) != len(impacts))):
        print("The number of weights or impacts provided do not meet the requirements.")
    
    for x in impacts:
        if x not in ['+','-']:
            print("The value of the impacts provided should be either '+' or '-'.")

    path_name_result = sys.argv[4]
    df1 = vector_normalise(df1)                               
    df1 = weighted_matrix(df1)                                
    ideal_values(df1)                                          
    df = performance_score(df1, df)                            
    df['Rank'] = df['Topsis Score'].rank(ascending=False)      
    df.to_csv(path_name_result, index=False)        


if __name__ == "__main__":
    main()

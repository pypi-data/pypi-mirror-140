import numpy as np
import pandas as pd
import sys
def create_matrix(matrix):
    matrix=matrix[:,1:]
    return matrix

def normalize(matrix,weight):
    column_squared_sum=np.zeros(matrix.shape[1])
    for j in range(matrix.shape[1]):
        for i in range(matrix.shape[0]):
            column_squared_sum[j]+=matrix[i][j]*matrix[i][j]
        column_squared_sum[j]=np.sqrt(column_squared_sum[j])
        matrix[:,j:j+1]=matrix[:,j:j+1]/column_squared_sum[j]

    return normailze_matrix(matrix,weight=np.asarray(weight))
def normailze_matrix( matrix,weight):
    totalweight=np.sum(weight)
    weight=weight/totalweight
    normailze_matrix=weight*matrix
    return normailze_matrix

def cases(normailze_matrix,is_max_the_most_desired):
    ideal_best=np.zeros(normailze_matrix.shape[1])
    ideal_worst = np.zeros(normailze_matrix.shape[1])
    for j in range(normailze_matrix.shape[1]):
        if is_max_the_most_desired[j]==1:
            ideal_best[j]=np.max(normailze_matrix[:,j])
            ideal_worst[j] = np.min(normailze_matrix[:, j])
        else:
            ideal_worst[j] = np.max(normailze_matrix[:, j])
            ideal_best[j] = np.min(normailze_matrix[:, j])
    return Euclidean(normailze_matrix,ideal_best,ideal_worst)

def Euclidean(matrix, ideal_best,ideal_worst):
    euclidean_best=np.zeros(matrix.shape[0])
    euclidean_worst=np.zeros(matrix.shape[0])
    for i in range(matrix.shape[0]):
        eachrowBest=0
        eachRowWorst=0
        for j in range(matrix.shape[1]):
            eachrowBest+=(matrix[i][j]-ideal_best[j])**2
            eachRowWorst+= (matrix[i][j] - ideal_worst[j])**2
        euclidean_best[i]=np.sqrt(eachrowBest)
        euclidean_worst[i]=np.sqrt(eachRowWorst)
    return performance_score(matrix,euclidean_best,euclidean_worst)

def performance_score(matrix,euclidean_best,euclidean_worst):
    performance=np.zeros(matrix.shape[0])
    for i in range( matrix.shape[0]):
        performance[i]=euclidean_worst[i]/(euclidean_best[i]+euclidean_worst[i])
    return performance

def topsis():
    try:
        filename=sys.argv[1]
    except:
        print('please provide  4 arguements as inputData.csv weights impacts outputFile.csv')
        sys.exit(1)
    
    try:
        weight_input = sys.argv[2]
    except:
        print('please provide 3 more arguement')
        sys.exit(1)
    
    try:
        impacts = sys.argv[3]
    except:
        print('please provide 2 more  arguement')
        sys.exit(1)
    try:
        impacts = sys.argv[3]
    except:
        print('please provide 1 more  arguement')
        sys.exit(1)
    try:
        df = pd.read_csv(filename)
    except:
        print('Could not read the file given by you')
    
    number_columns=len(df.columns)
    if number_columns<3:
        raise Exception("Less Col")
    
    
    if len(sys.argv)!=5:
        raise Exception("WrongInput")


    if df.isnull().sum().sum()>0:
        raise Exception("Blank")
        
    outputFileName = sys.argv[4]
    matrix = df.values
    original_matrix=matrix
    try:
     impacts_1=list(e for e in impacts.split(','))
     impact_final =[]
     for i in impacts_1 :
         if(i=='+'):
             impact_final.append(1)
         elif(i=='-'):
            impact_final.append(0)
         else:
             raise Exception('Impacts must be + or -')

   
    except:
        print('could not correctly parse correctly impacts arguement ')
    try:
        weights=list(float(w) for w in weight_input.split(','))
    except:
        print(" could not correctly parse weigths argument")

    matrix=create_matrix(matrix)
    
    normailze_matrix=normalize(matrix,weights)
    performance=cases(normailze_matrix,np.asarray(impact_final))
    l = list(performance)
    rank = [sorted(l, reverse=True).index(x) for x in l]
    
    df['Score'] = performance
    df['Rank'] = rank
    df['Rank'] = df['Rank'] + 1
    df.to_csv(outputFileName)

topsis()
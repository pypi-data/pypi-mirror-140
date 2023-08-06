import numpy as np
import pandas as pd
import sys
def create_mat(mat):
    mat=mat[:,1:]
    return mat

def normalize(mat,weight):
    column_squared_sum=np.zeros(mat.shape[1])
    for j in range(mat.shape[1]):
        for i in range(mat.shape[0]):
            column_squared_sum[j]+=mat[i][j]*mat[i][j]
        column_squared_sum[j]=np.sqrt(column_squared_sum[j])
        mat[:,j:j+1]=mat[:,j:j+1]/column_squared_sum[j]

    return normailze_matrix(mat,weight=np.asarray(weight))
def normailze_matrix( mat,weight):
    totalweight=np.sum(weight)
    weight=weight/totalweight
    # print(weight)
    # print(mat.shape)
    normailze_mat=weight*mat
    return normailze_mat

def cases(normailze_mat,is_max_the_most_desired):
    ideal_best=np.zeros(normailze_mat.shape[1])
    ideal_worst = np.zeros(normailze_mat.shape[1])
    for j in range(normailze_mat.shape[1]):
        if is_max_the_most_desired[j]==1:
            ideal_best[j]=np.max(normailze_mat[:,j])
            ideal_worst[j] = np.min(normailze_mat[:, j])
        else:
            ideal_worst[j] = np.max(normailze_mat[:, j])
            ideal_best[j] = np.min(normailze_mat[:, j])
    return Euclidean(normailze_mat,ideal_best,ideal_worst)

def Euclidean(mat, ideal_best,ideal_worst):
    euclidean_best=np.zeros(mat.shape[0])
    euclidean_worst=np.zeros(mat.shape[0])
    for i in range(mat.shape[0]):
        eachrowBest=0
        eachRowWorst=0
        for j in range(mat.shape[1]):
            eachrowBest+=(mat[i][j]-ideal_best[j])**2
            eachRowWorst+= (mat[i][j] - ideal_worst[j])**2
        euclidean_best[i]=np.sqrt(eachrowBest)
        euclidean_worst[i]=np.sqrt(eachRowWorst)
    return performance_score(mat,euclidean_best,euclidean_worst)

def performance_score(mat,euclidean_best,euclidean_worst):
    performance=np.zeros(mat.shape[0])
    for i in range( mat.shape[0]):
        performance[i]=euclidean_worst[i]/(euclidean_best[i]+euclidean_worst[i])
    return performance

def topsis():
    try:
        filename=sys.argv[1]
    except:
        print('please provide  4 arguements as filename weight impacts outputFileName')
        sys.exit(1)
    # print(filename)
    try:
        weight_input = sys.argv[2]
    except:
        print('please provide 3 more arguement')
        sys.exit(1)
    # print(weight_input)
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
    mat = df.values
    original_matrix=mat
    try:
     impacts_1=list(e for e in impacts.split(','))
     impact_final =[]
     for i in impacts_1 :
         if(i=='+'):
             impact_final.append(1)
         else:
             impact_final.append(0)

    #  print(impact_final)
    #  print("impacts")
    except:
        print('could not correctly parse correctly impacts arguement ')
    try:
        weights=list(float(w) for w in weight_input.split(','))
    except:
        print(" could not correctly parse weigths argument")

    mat=create_mat(mat)
    # print(mat)
    normailze_mat=normalize(mat,weights)
    performance=cases(normailze_mat,np.asarray(impact_final))
    l = list(performance)
    rank = [sorted(l, reverse=True).index(x) for x in l]
    # print("perfrmance_score", "rank", sep="       ")
    # for i in range(mat.shape[0]):
    #     print(performance[i],rank[i]+1,sep="        ")
    df['Score'] = performance
    df['Rank'] = rank
    df['Rank'] = df['Rank'] + 1
    # print(df)
    df.to_csv(outputFileName)

# if __name__=='__main__':
#     topsis()

# if __name__=='__main__':
    # try:
    #     filename=sys.argv[1]
    # except:
    #     print('please provide  4 arguements as filename weight impacts outputFileName')
    #     sys.exit(1)
    # print(filename)
    # try:
    #     weight_input = sys.argv[2]
    # except:
    #     print('please provide 3 more arguement')
    #     sys.exit(1)
    # print(weight_input)
    # try:
    #     impacts = sys.argv[3]
    # except:
    #     print('please provide 2 more  arguement')
    #     sys.exit(1)
    # try:
    #     impacts = sys.argv[3]
    # except:
    #     print('please provide 1 more  arguement')
    #     sys.exit(1)
    # try:
    #     df = pd.read_csv(filename)
    # except:
    #     print('Could not read the file given by you')

    # number_columns=len(df.columns)
    # if number_columns<3:
    #     raise Exception("Less Col")
    
    
    # if len(sys.argv)!=5:
    #     raise Exception("WrongInput")


    # if df.isnull().sum().sum()>0:
    #     raise Exception("Blank")
        
    # outputFileName = sys.argv[4]
    # mat = df.values
    # original_matrix=mat
    # try:
    #  impacts_1=list(e for e in impacts.split(','))
    #  impact_final =[]
    #  for i in impacts_1 :
    #      if(i=='+'):
    #          impact_final.append(1)
    #      else:
    #          impact_final.append(0)

    #  print(impact_final)
    #  print("impacts")
    # except:
    #     print('could not correctly parse correctly impacts arguement ')
    # try:
    #     weights=list(float(w) for w in weight_input.split(','))
    # except:
    #     print(" could not correctly parse weigths argument")

    # mat=create_mat(mat)
    # print(mat)
    # normailze_mat=normalize(mat,weights)
    # performance=cases(normailze_mat,np.asarray(impact_final))
    # l = list(performance)
    # rank = [sorted(l, reverse=True).index(x) for x in l]
    # print("perfrmance_score", "rank", sep="       ")
    # for i in range(mat.shape[0]):
    #     print(performance[i],rank[i]+1,sep="        ")
    # df['Score'] = performance
    # df['Rank'] = rank
    # print(df)
    # df.to_csv(outputFileName)

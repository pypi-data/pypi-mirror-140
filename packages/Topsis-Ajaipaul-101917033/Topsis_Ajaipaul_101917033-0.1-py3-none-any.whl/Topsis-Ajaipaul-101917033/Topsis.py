import sys
import math
import pandas as pd
import scipy.stats as ss


def Topsis(fileName,weights,impact,resultFile):
    try:
        mat = pd.read_csv(fileName)
        # mat1=mat
    except:
        raise Exception("File not found")
    
    rowN=mat.shape[0]
    colN=mat.shape[1]
    # print(mat)
    # print(weights)
    # print(impact)
    # print(colN)
    # print(rowN)
    if(len(weights)<colN-1 and len(impact)<colN-1):
        raise Exception("less number of weights and impacts assigned")
    if(len(weights)>colN-1 and len(impact)>colN-1):
        raise Exception("more number of weights and impacts assigned")
    if(len(weights)<colN-1):
        raise Exception("less number of weights assigned")
    if(len(weights)>colN-1):
        raise Exception("more number of weights assigned")

    if(len(impact)<colN-1):
        raise Exception("less number of impacts assigned")
    if(len(impact)>colN-1):
        raise Exception("more number of impacts assigned")

    # mat.astype('float32')            ##To convert the whole dataset into float 


    rms=[]
    for i in range(1,colN):
        s=0
        for j in range(rowN):
            s=s+float(mat.iloc[j][i]**2)
        s=float(math.sqrt(s))
        rms.append(s)
    
    for i in range(1,colN):
        for j in range(rowN):
            if(float(rms[i-1])==0.0):
                raise Exception("Division by zero not possible.")
            a=mat.iloc[j,i]/float(rms[i-1])
            mat.iloc[j,i]=a
    
    for i in range(1,colN):
        for j in range(rowN):
            a=mat.iloc[j,i]*weights[i-1]
            mat.iloc[j,i]=a

    best=[]
    worst=[]
    
    for i in range(1,colN):
        if impact[i-1]=='+':
            best.append(mat.iloc[:,i].max())
            worst.append(mat.iloc[:,i].min())
        else:
            worst.append(mat.iloc[:,i].max())
            best.append(mat.iloc[:,i].min())
    
    #euclidean distance
    
    performance=[]
    for i in range(rowN):
        sum_pos=sum((mat.iloc[i,1:]-best[:])**2)
        sum_neg=sum((mat.iloc[i,1:]-worst[:])**2)
           
        sum_pos=math.sqrt(sum_pos)
        sum_neg=math.sqrt(sum_neg)
        sums=sum_pos + sum_neg
        perf=sum_neg/sums
        performance.append(perf)


    # print(performance)
    
    ranks=[sorted(performance,reverse=True).index(x)+1 for x in performance]
    # print(ranks)
    mat1=pd.read_csv(fileName)
    mat1["Performance Score"] = performance    
    mat1["Ranks"]=ranks
    mat1.to_csv(resultFile,index=False)
    # print(mat1)
    # DataFrame.rank(axis=0, method='average', ascending=True)
    # ranks = sorted(list(range(1,len(performance)+1)))
    # print(ranks)
    # print(mat)
    

if(len(sys.argv)<5):
    raise Exception("Less inputs given")

if(len(sys.argv)>5):
    raise Exception("More inputs given")

fName=sys.argv[1]
weights=sys.argv[2]
impact=sys.argv[3]
resultFile=sys.argv[4]

w = list(weights.split(","))
w1=[float(i) for i in w]
imp=list(impact.split(","))

weights=[]
for i in range(len(w1)):
    weights.append(w1[i]/sum(w1))

for i in imp:
    if(i=='+' or i=='-'):
        continue
    else:
        raise Exception("Invalid impact input")

Topsis(fName,weights,imp,resultFile)
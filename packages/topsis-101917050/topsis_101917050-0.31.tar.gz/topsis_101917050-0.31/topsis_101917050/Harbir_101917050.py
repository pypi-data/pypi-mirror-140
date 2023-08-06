import sys
import pandas as pd
import numpy as np

def topsis(file,weight,impact,output):

    ## Handling invalid file type exception
    if(file.split('.')[-1]!='csv'):
        print("[ERROR]File extension not supported! Must be csv flie")
        exit(0)
    
    ## Handling File not present exception
    try:
        df=pd.read_csv(f'./{file}')
    except :
        print(f'[ERROR]{file} does not exist!s')
        sys.exit(0)
    
    models=df.iloc[:,0].values.tolist()
    data=df.iloc[:,1:].values.tolist()
    # print(data)
    # print(weight)

    ## Handling insufficient number of columsn exception
    if len(data[0])<3:
        print("[Error]Insufficient number of columns must be atleast 3")
        sys.exit(0)

    ## Handling Wrong weights format exception
    try:
        weights=list(map(int,weight.strip().split(',')))
    except:
        print("[ERROR] weights must be provided in format '1,0.5,2,1' and seperated by ',' and all weights must be numeric values")
        sys.exit(0)
    # print(type(weights))
    # print(len(data[0]))

    ## Handling Wrong number of weights exception
    if(len(weights)!=len(data[0])):
        print(f"[ERROR]Number of weights should be :{len(data[0])}")
        sys.exit(0)
    
    ## Handling negative weights exception
    if any(x <0 for x in weights):
        print("[ERROR] Weights Must be positive")
        sys.exit(0)
    
    ## Handling Wrong Impacts format exception
    try:
        impacts=list(impact.strip().split(','))
    except:
        print("[ERROR] impacts must be provided in format '+,-,+,-,+' and seperated by ','")
        sys.exit(0)
    # print(impacts)

    ## Handling Wrong number of impacts exception
    if(len(impacts)!=len(data[0])):
        print(f"[ERROR]Number of impacts should be :{len(data[0])}")
        sys.exit(0)

    ## Handling of impact either + or - exception
    signs='+-'
    if any(x not in signs for x in impacts):
        print("[ERROR] impacts can only be '+' or '-'")
        sys.exit(0)

    # -------------- 1. Calculating Root Mean Square of each column -------------- #
    # print(data)
    rms=[0]*(len(data[0]))
    for i in range(len(data[0])):
        for j in range(len(data)):
            rms[i]=rms[i]+data[j][i]**2
        rms[i]=(rms[i])**(1/2)
            
    # print(rms)
    # ------------------------ 2 . Noramalization of data ------------------------ #
    normalised=[]
    for i in range(len(data)):
        l = list()
        for j in range(len(data[0])):
            l.append(data[i][j]/rms[j])
        normalised.append(l)
    # print(noramalised)

    # -------------------------- 3. Calculating Weights -------------------------- #
    s=sum(weights)
    # print(weights)
    for i in range(len(weights)):
        weights[i]/=s
    # print(weights)

    # --------------------- 4. Multiplying data with weights --------------------- #
    # print(noramalised)
    for i in range(len(data[0])):
        for j in range(len(data)):
            normalised[j][i]*=weights[i]
    
    # print(noramalised)

    # ----------------- 5. Calculating Ideal Best and Ideal Worst ---------------- #
    idealBest=[]
    idealWorst=[]

    for i in range(len(normalised[0])):
        if(impacts[i]=='+'):
            idealBest.append(np.max([ x[i] for x in normalised] ))
            idealWorst.append(np.min([ x[i] for x in normalised] ))
        if(impacts[i]=='-'):
            idealWorst.append(np.max([ x[i] for x in normalised] ))
            idealBest.append(np.min([ x[i] for x in normalised] ))
    
    # print(idealBest)
    # print(idealWorst)   
    # for i in range(len(normalised)):
    #     for j in range(len(normalised[0])):
    #         print(normalised[i][j],end=" ")
    #     print()
    
    # --------------------- 6. Calculating Performance Score --------------------- #
    performance=[]
    for i in range(len(normalised)):
        pos=0
        neg=0
        for j in range(len(normalised[0])):
            pos+=(normalised[i][j]-idealBest[j])**2
            neg+=(normalised[i][j]-idealWorst[j])**2
        pos=pos**(1/2)
        neg=neg**(1/2)
        performance.append(neg/(neg+pos))
    
    ranks = sorted(list(range(1,len(performance)+1)))
    pt=sorted(performance,reverse=True)

    data2=[]
    for i in range(len(data)):
        data[i].append(performance[i])
        data[i].append(ranks[pt.index(performance[i])])
        l=[]
        l.append(models[i])
        l.extend(data[i])
        data2.append(l)

    cols=list(df.columns)
    cols.extend(['Topsis Score','Rank'])

    final=[]
    # print(final)

    for i in range(len(data)):
        final.append(data2[i])
    
    # print(final)
    final=pd.DataFrame(final,columns=cols,index=None)

    ## Handling wrong output filename exception
    if(output.split('.')[-1]!='csv'):
        print("[ERROR]File extension for output filename not supported! Must be csv flie")
        exit(0)
    path=f"101917050-{output}"

    final.to_csv(path)


def main(filename,output):
    # args=sys.argv
    # argLen=len(args)
    weight=input("Enter weights (seperated by comma) :")
    impact=input("Enter impacts(+/-) seperated by comma :")
    topsis(filename,weight,impact,output)
    # ## Handling Wrong number of arguments exception
    # if(argLen!=5):
    #     print("[ERROR]Invalid number of arguments")
    #     sys.exit(0)
    # else :
    #     topsis(args[1],args[2],args[3],args[4])




# if __name__=='__main__':
#     main(filename,output)
   

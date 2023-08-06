import pandas as pd
import math
import sys

def func(a,b,c):

    # if len(sys.argv) != 5:
    # print("Number of Arguments Must Be 5")
    # quit()
    
    filepath=a
    try:
        wt=b
        wt=wt.split(',')
        wt=[int(s) for s in wt]
    except:
        print("Weights Must Be Comma Seperated")
        quit()

    # impacts=['+','+','-','+','+']
    try:
        impacts=c
        impacts=impacts.split(',')
        # impacts=[int(s) for s in impacts]
    except:
        print("Impacts Must Be Comma Seperated")
        quit()

    try:
        df=pd.read_csv(filepath)
        # df.info()
        # df.head(10)
        ncol = df.shape[1]
        # assert len(decision.shape) == 2, "Decision matrix must be two dimensional"
        # assert len(weights.shape) == 1, "Weights array must be one dimensional"
        if ncol<3:
            print("Number of Columns should be three or more")
            quit()
        if len(wt)!=ncol-1:
            print("Wrong length of Weights array, should be {}".format(ncol-1))
            quit()
        if len(impacts)!=ncol-1:
            print("Wrong length of Impacts array, should be {}".format(ncol-1))
            quit()
        if len(df.dtypes[df.dtypes != 'int64'][df.dtypes != 'float64']) != 1:
            print("Incorrect Number Of Non-Numeric Columns present")
            quit()
        
        imp=["+","-"]
        result =  all(elem in imp  for elem in impacts)

        if result==False:
            print("Impact Can only be + or -")
            quit()


        li=[]
        for i in range(1,len(df.columns)):
            # print(df.iloc[0,i])
            li.append(math.sqrt((df[df.columns[i]]**2).sum()))


        # li

        # df.head(5)


        for i in range(1,len(df.columns)):
            # print(len(df))
            # print(i)
            for j in range(len(df)):
                df.iloc[j,i]=(df.iloc[j,i]/li[i-1])*wt[i-1]


        v_best=[]
        v_worst=[]
        for i in range(1,len(df.columns)):
            pz=[]
            pz.append(max(df.iloc[:,i]))
            pz.append(min(df.iloc[:,i]))
            if impacts[i-1]=='+':
                v_best.append(pz[0])
                v_worst.append(pz[1])
            else:
                v_best.append(pz[1])
                v_worst.append(pz[0])    

        frm_best=[]
        frm_worst=[]
        for i in range(len(df)):
            x=0
            y=0
            # print(i)
            for j in range(1,len(df.columns)):
                x=x + (df.iloc[i,j]-v_best[j-1])**2
                y=y + (df.iloc[i,j]-v_worst[j-1])**2  
            frm_best.append(math.sqrt(x))
            frm_worst.append(math.sqrt(y))

        performance=[]
        for i in range(len(df)):
            performance.append((frm_worst[i]/(frm_best[i] + frm_worst[i])))
        df['Topsis Score']=performance

        df['Rank'] = df['Topsis Score'].rank(ascending = False)
        df.sort_values("Rank",inplace=True,ignore_index=True)
        # df.head(10)
        print(df.head(10))

    except FileNotFoundError:
        print("Wrong file or file path")
        quit()


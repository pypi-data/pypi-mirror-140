import sys
import numpy as np
import copy as copy
import pandas  as pd

def topsis(df, wgt, impt):
    
    colmns = df.columns
    india = df.index
    ilen=len(df.index)
    for k in range(1,len(colmns)):
        df[colmns[k]] = pd.to_numeric(df[colmns[k]], downcast="float")

    for i in range(len(wgt)):
        wgt[i] = float(wgt[i])

    siqure = []
    for k in colmns[1:]:
        terabyt = 0
        for l in range(ilen):
            terabyt += np.square(float(df.iloc[l][k]))
        siqure.append(terabyt)

    ind=0
    df_list = []
    for k in colmns[1:]:
        lits = []
        for l in range(len(india)):
            a = float(df.iloc[l][k] / np.sqrt(siqure[ind]))
            lits.append(a)

        df_list.append(lits)
        ind+=1

    onew_df = pd.DataFrame()
    
    onew_df[colmns[0]] = df[colmns[0]]


    for val in range(len(df_list)):
        onew_df[colmns[val+1]] = df_list[val]

    df = onew_df

#########
    df_list = []
    ind=0
    for k in colmns[1:]:
        lits = []
        for l in range(ilen):
            a = df.iloc[l][k] * (wgt[ind])
            lits.append(a)
        df_list.append(lits)
        ind+=1

    onew_df = pd.DataFrame()
    onew_df[colmns[0]] = df[colmns[0]]

    for val in range(len(df_list)):
        onew_df[colmns[val+1]] = df_list[val]

    df = onew_df
########
    maxm = ['Ideal Best']
    minm = ['Ideal Worst']

    for ind in colmns[1:]:
        column = df[ind]  
        val_min = column.min()
        minm.append(val_min)
        val_max = column.max()
        maxm.append(val_max)
    ind=1
    for k in impt:
        if k=='-':
            # maxm[ind],  minm[ind]=minm[ind], maxm[ind]
            temp = maxm[ind]
            maxm[ind] = minm[ind]
            minm[ind] = temp
        ind+=1
          
    df.loc[ilen] = maxm
    df.loc[len(df.index)] = minm
###################
    simple_max = []
    simple_min = []

    for ind2 in range(len(df.index) - 2):
        max_temp = 0
        min_temp = 0
        for ind1 in colmns[1:]:
            min_temp += np.square(df.iloc[ind2][ind1] - df.iloc[-1][ind1])
            max_temp += np.square(df.iloc[ind2][ind1] - df.iloc[-2][ind1])

        simple_min.append(round(np.sqrt(min_temp),4))
        simple_max.append(round(np.sqrt(max_temp),4))

        
##################
    df = df.iloc[:-2 , :]
    smx_len=len(simple_max)
    smn_len=len(simple_min)
    s_avg = []
    for ind3 in range(smx_len):
        s_avg.append((simple_max[ind3] + simple_min[ind3]))

    cent_per = []
    for i in range(smn_len):
        cent_per.append((simple_min[i]/s_avg[i]))
        
    df = df.assign(Topsis_Score =cent_per)
    # assigning rank to it 
    df['Rank'] = df['Topsis_Score'].rank(ascending = 0)

    king_of_ranks = []
    for ind5 in range(ilen):
        king_of_ranks.append(int(df.loc[ind5]['Rank']))
            
    df.drop(['Rank'], axis = 1)

    df['Rank'] = king_of_ranks
    
    return df


def main():
    
    n=len(sys.argv)
    if n==5:
        try:
            file=sys.argv[1]
            df=pd.read_csv(file)
        except:
            print("error in file(file must be csv) or filename")
            sys.exit()
        anycol=df.columns[0]
        df.set_index(anycol,inplace=True)

        df.shape[1] == df.select_dtypes(include=np.number).shape[1]

        if(df.shape[1]==5):
            subject1=0
            subject2=0
            for val in sys.argv[2]:
                if(val.isnumeric()==False and val!=',' and val!='.' ):
                    subject1=subject1+1
            for val in sys.argv[3]:
                if(val.isnumeric()==False and val!='+' and val!='-' and val!=',' and val!='.'):
                    subject2=subject2+1

            if(subject1!=0 or subject2!=0):
                print("Impacts and weights must be separated by (comma)")
                sys.exit()

            w=[float(i) for i in sys.argv[2].split(',')]
            im=[str(i) for i in sys.argv[3].split(',')]
            output=sys.argv[4]
            l=len(df.columns)
            if(l>=3):
                if(len(im)!=l or len(w)!=l):
                    print("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same")
                    sys.exit()

                for i in range(0,len(im)):
                    if(im[i]!='+' and im[i]!='-'):
                        print("Impacts must be either +ve or -ve not ",im[i])
                        sys.exit()
                
                inFile = sys.argv[1]
                weight = sys.argv[2]
                impact = sys.argv[3]
                result_file = sys.argv[4]
                impact_li = impact.split(',')
                weight_li = weight.split(',')
                df = pd.read_csv(inFile)

                result = topsis(df, weight_li, impact_li)
                result.to_csv(result_file)
            else:
                print("Input file must contain three or more columns")
                sys.exit()

        else:
            print("Handling of non-numeric values")
            sys.exit()

    else:
        print("wrong no of inputs please pass in the form of {python_file_name inputFileName  Weights  Impacts resultFileName ")
        sys.exit()





if __name__ == '__main__':
    main()
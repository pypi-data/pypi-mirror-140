# Name: Siddharth Juyal
# Roll Number: 101903218
# Batch: 3COE8
#------------------------------------------------------------------------------------------------------#

#import necessary libraries
import sys
import numpy as np
import pandas as pd

class Error(Exception):
    pass
class WrongNumberOfParameters(Error):
    val=0
    def __init__(self,val):
        g=open("101903218-log.txt","w")
        g.write("You have entered wrong number Of Parameters! \n")
        g.write("You entered "+str(val)+" number of Parameters while only Two were required.")
        g.close()
class IncorrectColumns(Error):
    pass
class NoComma(Error):
    pass
class WrongImpacts(Error):
    pass
class WrongNumberOfValues(Error):
    def __init__(self,columns,weights,impacts):
        g=open("101903218-log.txt","w")
        g.write("You have Entered Wrong Number Of Values! Kindly Check the input Parameters again! \n")
        g.write("Length of Columns "+str(columns)+"\n")
        g.write("Length of Weights "+str(weights)+"\n")
        g.write("Length of Impacts "+str(impacts)+"\n")
        g.close()

class topsis_cal:

    def normalization(self,df):
        for i in df.columns[1:]:
            rss=0
            rss=(round(sum([ j*j for j in df[i]]),2))
            rss=rss**0.5
            df[i]=(df[i]/rss)
            df[i]=[ round(j,4) for j in df[i]]

    def Weight_Assignment(self,df,weights):
        for i,k in enumerate(df.columns[1:],0):
            df[k]=(df[k]*weights[i])
            df[k]=[ round(j,5) for j in df[k]]
    
    def Find_pscore(self,df,impacts):
        pscore=[]
        for j in range(len(df)):
            sp=0
            sn=0
            for i in range(len(df.columns)-1):
                if(impacts[i]=='+'):
                    mini=min(df.iloc[:,i+1])
                    maxm=max(df.iloc[:,i+1])
                    sp+=(df.iloc[j,i+1]-maxm)**2
                    sn+=(df.iloc[j,i+1]-mini)**2
                else:
                    mini=min(df.iloc[:,i+1])
                    maxm=max(df.iloc[:,i+1])
                    sp+=(df.iloc[j,i+1]-mini)**2
                    sn+=(df.iloc[j,i+1]-maxm)**2
            sp=sp**0.5
            sn=sn**0.5
            pscore.append(sn/(sn+sp))
        df["Topsis_Score"]=[round(i,5) for i in pscore]
        df["Rank"]=[sorted(pscore,reverse=True).index(i)+1 for i in pscore]

    def topsis(self,df,weights,impacts):
        self.normalization(df)
        self.Weight_Assignment(df,weights)
        self.Find_pscore(df,impacts)

def check_nonnumeric(df):
    nonnumeric=[]
    for i in range(1,len(df.columns)):
        for j in range(len(df.iloc[:,i])):
            try:
                df.iloc[j,i]=float(df.iloc[j,i])
            except:
                nonnumeric.append(j)
    nonnumeric=[df.index[j] for j in nonnumeric]
    df=df.drop(nonnumeric)
    return df

try:
    n=len(sys.argv)
    if n!=5:
        raise WrongNumberOfParameters(n)
    filename=sys.argv[1]
    weights=sys.argv[2]
    impacts=sys.argv[3]
    outputname=sys.argv[4]
    try:
        weights=[float(i) for i in weights.split(',')]
    except:
        raise NoComma
    impacts=impacts.split(',')
    for i in impacts:
        if(i!='+' and i!='-' ):
            raise WrongImpacts
    df=pd.read_csv(filename)
    if(len(df.columns)<3):
        raise IncorrectColumns
    if(len(df.columns)-1!=len(impacts) or len(impacts)!=len(weights)):
        raise WrongNumberOfValues(len(df.columns),len(impacts),len(weights))
    df=df.dropna(subset=df.columns)
    df=check_nonnumeric(df)   
    df=df.dropna(subset=df.columns)
    fin=topsis_cal()
    fin.topsis(df,weights,impacts)
    g=open("101903218-log.txt","w")
    g.write("Successfully Executed with no error! ")
    g.close()
    df.to_csv(outputname)

except FileNotFoundError:
    g=open("101903218-log.txt","w")
    g.write("File Name Does not Exist! ")
    g.close()
except IncorrectColumns:
    g=open("101903218-log.txt","w")
    g.write("File Does Not Contains More than 3 Columns! ")
    g.close()
except WrongNumberOfValues:
    pass
except NoComma:
    g=open("101903218-log.txt","w")
    g.write("Values entered are not seperated by comma(',')! ")
    g.close()
except WrongImpacts:
    g=open("101903218-log.txt","w")
    g.write("Values entered for impacts are incorrect! ")
    g.close()
except WrongNumberOfParameters:
    pass
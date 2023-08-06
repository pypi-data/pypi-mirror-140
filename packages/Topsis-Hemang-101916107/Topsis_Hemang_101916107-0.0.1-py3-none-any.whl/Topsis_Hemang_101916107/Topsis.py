import numpy as np
import pandas as pd
import os
import sys
import logging


logging.basicConfig(filename='101916107-log.log',filemode='w',format='%(name)s - %(levelname)s - %(message)s')

if not len(sys.argv)>4:
    logging.error("EXPECTED 4 ARGUMENTS")
    print("EXPECTED 4 ARGUMENTS")
    sys.exit()

if not os.path.exists(sys.argv[1]):
    logging.error("FILE NOT FOUND")
    print("FILE NOT FOUND")
    sys.exit()

class nonnumeric:
        def fun(data,cols):
                for i in range(1,cols):
                        pd.to_numeric(data.iloc[:,i],errors='coerce')
                        data.iloc[:,i].fillna((data.iloc[:,i].mean()),inplace=True)
                return data

class checkwt:
        def fun():
                try:
                        weights=[int(i) for i in sys.argv[2].split(',')]
                        return weights
                except:
                        logging.error("Weight array Expected!!")
                        print("Weight array Expected!!")
                        sys.exit()

class checkimpact:
        def fun():
                try:
                        impacts=sys.argv[3].split(',')
                        for i in impacts:
                                if not (i=='+' or i=='-'):
                                        logging.error("expected + or - in impact array")
                                        print("expected + or - in impact array")
                                        sys.exit()
                        return impacts
                except:
                        logging.error("expected impact array")
                        print("expected impact array")
                        sys.exit()


class columns:
        def fun(wts, impacts, cols):
                if (cols-1)!=len(wts):
                        logging.error("incorrect number of weights")
                        print("incorrect number of weights")
                        return False
                if (cols-1)!=len(impacts):
                        logging.error("incorrect number of impacts")
                        print("incorrect number of impacts")
                        return False
                return True
                

    
class normalize:
        def fun(data,cols,wts):
                for i in range(1,cols):
                        temp=0
                for j in range(len(data)):
                        temp+=data.iloc[j,i]**2
                temp**=0.5
                for j in range(len(data)):
                        data.iat[j,i]=(data.iloc[j,i]/temp)*wts[i-1]
                return data

class impact:
        def fun(data,cols,impacts):
                positiveSolution=(data.max().values)[1:]
                negativeSolution=(data.min().values)[1:]
                for i in range(1,cols):
                        if impacts[i-1]=='-':
                                positiveSolution[i-1],negativeSolution[i-1]=negativeSolution[i-1],positiveSolution[i-1]
                return positiveSolution,negativeSolution

def funTopsis(dataset,cols,wts,impacts,fileName='output.csv'):
        if not len(dataset.columns.values)==cols:
                logging.error("incorrect number of columns")
                print("incorrect number of columns")
                sys.exit()
                
        if not columns.fun(wts,impacts,cols):
                sys.exit()
    
        tempdata=dataset

        tempdata=normalize.fun(tempdata,cols,wts)
 
        pos,neg=impact.fun(tempdata,cols,impacts)
   
        topsisScore=[]
        for i in range(len(tempdata)):
                temppos,tempneg=0,0
                for j in range(1,cols):
                        temppos+=(pos[j-1]-tempdata.iloc[i,j])**2
                        tempneg+=(neg[j-1]-tempdata.iloc[i,j])**2
                temppos,tempneg=temppos**0.5,tempneg**0.5
                topsisScore.append(tempneg/(temppos+tempneg))
        dataset['Topsis Score']=topsisScore
 
        dataset['Rank']=(dataset['Topsis Score'].rank(method='max',ascending=False))
        dataset=dataset.astype({"Rank":int})
        dataset.to_csv(fileName,index=False)

def reading():
    data=pd.read_csv(sys.argv[1])

    cols=len(data.columns.values)
    data=nonnumeric.fun(data,cols)
    wts=checkwt.fun()
    
    impacts=checkimpact.fun()
    if not columns.fun(wts,impacts,cols):
        sys.exit()

    if((os.path.splitext(sys.argv[4]))[1]!=".csv"):
        logging.log("expected a csv output filename")
        print("expected a csv output filename")
        sys.exit()
    if(os.path.isfile(sys.argv[4])):
        os.remove(sys.argv[4])
     
    obj=funTopsis(data,cols,wts,impacts,sys.argv[4])

if __name__ == "__main__":
    reading()
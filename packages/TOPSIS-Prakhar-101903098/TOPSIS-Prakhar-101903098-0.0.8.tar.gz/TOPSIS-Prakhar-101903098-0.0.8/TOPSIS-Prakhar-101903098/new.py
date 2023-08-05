import pandas as pd
import numpy as np
from sklearn import preprocessing
import sys
class WrongNumberOfParameters(Exception):
    pass
class NumberOfColumnError(Exception):
    pass
class UnequalWeightandImpacts(Exception):
    pass
class IncorrectImpact(Exception):
    pass
def topsis():
    try:
        if len(sys.argv)>4:
            raise WrongNumberOfParameters("ERROR : Incorrect Number of Parameters detected...")
        dataf=pd.read_csv(sys.argv[1])
        if len(dataf.columns)<3:
            raise NumberOfColumnError("ERROR : Input dataset has less than 3 columns...")
        finaldf=dataf
        dataf=dataf.iloc[:,1:]
        sz=len(dataf)
        impacts=sys.argv[3]
        weights=sys.argv[2]
        if len(impacts.split(sep=","))!=len(weights.split(sep=",")):
            raise UnequalWeightandImpacts("ERROR : Size of weight and impact is not same...")
        if len(impacts.split(sep=","))!=len(dataf.columns):
            raise UnequalWeightandImpacts("ERROR : Size of dataset and impact is not same...")
        if len(weights.split(sep=","))!=len(dataf.columns):
            raise UnequalWeightandImpacts("ERROR : Size of dataset and weight is not same...")
        
        ideal_best=[]
        ideal_worst=[]
        for i in dataf.columns:
            arr=dataf.loc[:,i]
            newarr=preprocessing.normalize(np.reshape(np.array(arr),(1,sz)))
            dataf.loc[:,i]=np.reshape(newarr,(sz,1))

            
        wlist=weights.split(sep=",")
        for i in range(len(dataf.columns)):
            dataf.iloc[:,i]*=float(wlist[i])
            
            
        ilist=impacts.split(sep=",")
        for point in ilist:
            if point not in ["+","-"]:
                raise IncorrectImpact("ERROR : Impact values are incorrect...")
            
        for i in range(len(dataf.columns)):
            if ilist[i]=="+":
                ideal_best=np.append(ideal_best,dataf.iloc[:,i].max())
                ideal_worst=np.append(ideal_worst,dataf.iloc[:,i].min())
            elif ilist[i]=="-":
                ideal_best=np.append(ideal_best,dataf.iloc[:,i].min())
                ideal_worst=np.append(ideal_worst,dataf.iloc[:,i].max())
        dataf=dataf.append(pd.Series(ideal_best,index=dataf.columns),ignore_index=True)
        dataf=dataf.append(pd.Series(ideal_worst,index=dataf.columns),ignore_index=True)

        dist_ib=[]
        dist_iw=[]
        for i in range(sz):
            sumplus=0
            summinus=0
            for j in dataf.columns:
                temp=dataf.loc[i,j]-dataf.loc[sz,j]
                sumplus+=np.power(temp,2)
                temp=dataf.loc[i,j]-dataf.loc[sz+1,j]
                summinus+=np.power(temp,2)
            dist_ib.append(np.sqrt(sumplus))
            dist_iw.append(np.sqrt(summinus))
        topsis=[]
        for i in range(len(dist_iw)):
            topsis.append(dist_iw[i]/(dist_iw[i]+dist_ib[i]))
        finaldf["Topsis Score"]=topsis
        dict_rank={}
        topsis.sort(reverse=True)
        dict_rank[topsis[0]]=1
        rank=2
        for i in range(1,len(topsis)):
            dict_rank[topsis[i]]=rank
            rank+=1
        rank_topsis=[]
        for i in finaldf["Topsis Score"]:
            rank_topsis.append(dict_rank[i])
        finaldf["Rank"]=rank_topsis
        finaldf.to_csv("101903098-result-1.csv",index=False)
        
    except WrongNumberOfParameters as wnop:
        print(wnop)
    except ValueError:
        print("ERROR : Incorrect value has been detected...")
    except FileNotFoundError:
        print("ERROR : Input file not found on the system...")
    except NumberOfColumnError as nce:
        print(nce)
    except UnequalWeightandImpacts as uwi:
        print(uwi)
    except IncorrectImpact as ii:
        print(ii)        
import pandas as pd
import numpy as np
from sklearn import preprocessing
from importlib import resources
import io
import sys

def topsis(inputFile, weights, impacts, outputFile = "101903773.csv"):
    class Incorrect_Params_no(Exception):
        pass
    class col_nos_error(Exception):
        pass
    class weight_error(Exception):
        pass
    class impact_error(Exception):
        pass    
    #exception handling


    try:


        dframe=pd.read_csv(inputFile)
        if len(dframe.columns)<3:
            raise col_nos_error("Input dataset has less than 3 columns,retry")
        dfl=dframe
        dframe=dframe.iloc[:,1:]
        sz=len(dframe)
        
        print(len(impacts.split(sep=",")), len(dframe.columns))

        if len(impacts.split(sep=","))!=len(weights.split(sep=",") ):
            raise weight_error("Weight and impact size different")
        if len(impacts.split(sep=","))!=len(dframe.columns):
            raise weight_error("Dataset and impact size different")
        if len(weights.split(sep=","))!=len(dframe.columns):
            raise weight_error("Dataset and weight size different")
        
        best=[]
        worst=[]
        #normalization of table
        for i in dframe.columns:
            arr=dframe.loc[:,i]
            newarr=preprocessing.normalize(np.reshape(np.array(arr),(1,sz)))
            dframe.loc[:,i]=np.reshape(newarr,(sz,1))

            
        wlist=weights.split(sep=",")
        for i in range(len(dframe.columns)):
            dframe.iloc[:,i]*=float(wlist[i])
        ilist=impacts.split(sep=",")
        for point in ilist:
            if point not in ["+","-"]:
                raise impact_error("ERROR : Impact values are incorrect...")
                
        for i in range(len(dframe.columns)):
            if ilist[i]=="+":
                best=np.append(best,dframe.iloc[:,i].max())
                worst=np.append(worst,dframe.iloc[:,i].min())
            elif ilist[i]=="-":
                best=np.append(best,dframe.iloc[:,i].min())
                worst=np.append(worst,dframe.iloc[:,i].max())
        dframe=dframe.append(pd.Series(best,index=dframe.columns),ignore_index=True)
        dframe=dframe.append(pd.Series(worst,index=dframe.columns),ignore_index=True)

        dist_ib=[]
        dist_iw=[]
        for i in range(sz):
            sumplus=0
            summinus=0
            for j in dframe.columns:
                temp=dframe.loc[i,j]-dframe.loc[sz,j]
                sumplus+=np.power(temp,2)
                temp=dframe.loc[i,j]-dframe.loc[sz+1,j]
                summinus+=np.power(temp,2)
            dist_ib.append(np.sqrt(sumplus))
            dist_iw.append(np.sqrt(summinus))
        topsis=[]
        for i in range(len(dist_iw)):
            topsis.append(dist_iw[i]/(dist_iw[i]+dist_ib[i]))
        dfl["Topsis Score"]=topsis
        dict_rank={}
        #rank determination
        topsis.sort(reverse=True)
        dict_rank[topsis[0]]=1
        rank=2
        for i in range(1,len(topsis)):
            dict_rank[topsis[i]]=rank
            rank+=1
        rank_topsis=[]
        for i in dfl["Topsis Score"]:
            rank_topsis.append(dict_rank[i])
        dfl["Rank"]=rank_topsis
        dfl.to_csv(outputFile,index=False)
    except Incorrect_Params_no as wnop:
        print(wnop)
    except ValueError:
        print("Incorrect value present")
    except FileNotFoundError:
        print("Input value not found")
    except col_nos_error as nce:
        print(nce)
    except weight_error as uwi:
        print(uwi)
    except impact_error as ii:
        print(ii)

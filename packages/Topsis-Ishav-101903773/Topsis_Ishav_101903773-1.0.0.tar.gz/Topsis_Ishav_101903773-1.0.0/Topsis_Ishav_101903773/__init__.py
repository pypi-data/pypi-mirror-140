#Ishav Gupta
#Roll No. 101903773
#3CO29
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
        Sz0=len(dframe)
        
        if len(impacts.split(sep=","))!=len(weights.split(sep=",") ):
            raise weight_error("Weight and impact size different")
        if len(impacts.split(sep=","))!=len(dframe.columns):
            raise weight_error("Dataset and impact size different")
        if len(weights.split(sep=","))!=len(dframe.columns):
            raise weight_error("Dataset and weight size different")
        
        best=[]
        worst=[]
        for i in dframe.columns:
            arr=dframe.loc[:,i]
            newarr=preprocessing.normalize(np.reshape(np.array(arr),(1,Sz0)))
            dframe.loc[:,i]=np.reshape(newarr,(Sz0,1))

            
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

        dist_between_best=[]
        dist_between_worst=[]
        for i in range(Sz0):
            add_sum=0
            sub_sum=0
            for j in dframe.columns:
                temp=dframe.loc[i,j]-dframe.loc[Sz0,j]
                add_sum+=np.power(temp,2)
                temp=dframe.loc[i,j]-dframe.loc[Sz0+1,j]
                sub_sum+=np.power(temp,2)
            dist_between_best.append(np.sqrt(add_sum))
            dist_between_worst.append(np.sqrt(sub_sum))
        topsis=[]
        for i in range(len(dist_between_worst)):
            topsis.append(dist_between_worst[i]/(dist_between_worst[i]+dist_between_best[i]))
        dfl["Topsis Score"]=topsis
        diction_ary={}
        topsis.sort(reverse=True)
        diction_ary[topsis[0]]=1
        rank=2
        for i in range(1,len(topsis)):
            diction_ary[topsis[i]]=rank
            rank+=1
        rank_topsis=[]
        for i in dfl["Topsis Score"]:
            rank_topsis.append(diction_ary[i])
        dfl["Rank"]=rank_topsis
        dfl.to_csv(outputFile,index=False)
    except Incorrect_Params_no as err1:
        print(err1)
    except ValueError:
        print("Incorrect value present")
    except FileNotFoundError:
        print("Input value not found")
    except col_nos_error as err2:
        print(err2)
    except weight_error as err3:
        print(err3)
    except impact_error as err4:
        print(err4)

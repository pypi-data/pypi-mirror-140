# Author
# Name:Sarthak  
# College: Thapar University Patiala
# 3rd Year Computer Engineering
# Roll-Number= 101903774
# Branch= 3COE1
import pandas as pd
import numpy as np
import math
import io
import sys
from sklearn import preprocessing
from importlib import resources

class Invalid_Number_Of_Parameters(Exception):
    pass
class Invalid_Number_Of_Columns(Exception):
    pass
class Unequal_Weights_And_Impacts(Exception):
    pass
class Incorrect_Impact(Exception):
    pass

#Exception handling

def topsis(inputFile, weights, impacts, outputFile = "101903774.csv"):
    try:
        # 1st parameter = Input Python File
        # 2nd parameter = Input csv file
        # 3rd parameter = Weights
        # 4th paramter = Impacts
        # 5th parameter (optional)= Output csv File

        # Reading the input csv file
        df=pd.read_csv(inputFile)
        if len(df.columns)<3:
            raise Invalid_Number_Of_Columns("Input dataset must have more than 3 columns!!")
        new_df=df
        top=[]
        bad=[]
        df=df.iloc[:,1:]
        size=len(df)
        if len(impacts.split(sep=","))!=len(weights.split(sep=",")):
            raise Unequal_Weights_And_Impacts("Weight and impact are of different sizes!!")
        if len(impacts.split(sep=","))!=len(df.columns):
            raise Unequal_Weights_And_Impacts("Dataset and impact are of different sizes!!")
        if len(weights.split(sep=","))!=len(df.columns):
            raise Unequal_Weights_And_Impacts("Dataset and weight are of different sizes!!")
        
        #Normalization of table
        for i in df.columns:
            arr=df.loc[:,i]
            newarr=preprocessing.normalize(np.reshape(np.array(arr),(1,size)))
            df.loc[:,i]=np.reshape(newarr,(size,1))

        wlist=weights.split(sep=",")
        for i in range(len(df.columns)):
            df.iloc[:,i]*=float(wlist[i])
        ilist=impacts.split(sep=",")
        for point in ilist:
            if point not in ["-","+"]:
                raise Incorrect_Impact("ERROR : Impact values are incorrect. Must be either + or - ")
                
        for i in range(len(df.columns)):
            if ilist[i]=="-":
                top=np.append(top,df.iloc[:,i].min())
                bad=np.append(bad,df.iloc[:,i].max())
            elif ilist[i]=="+":
                top=np.append(top,df.iloc[:,i].max())
                bad=np.append(bad,df.iloc[:,i].min())
        df=df.append(pd.Series(top,index=df.columns),ignore_index=True)
        df=df.append(pd.Series(bad,index=df.columns),ignore_index=True)

        best_dist=[]
        worst_dist=[]
        for val in range(size):
            x=0
            y=0
            for j in df.columns:
                temp=df.loc[val,j]-df.loc[size,j]
                x+=np.power(temp,2)
                temp=df.loc[val,j]-df.loc[size+1,j]
                y+=np.power(temp,2)
            worst_dist.append(math.sqrt(y))
            best_dist.append(math.sqrt(x))
        topsis=[]
        for val in range(len(worst_dist)):
            k=worst_dist[val]/(worst_dist[val]+best_dist[val])
            topsis.append(k)
        rank_dict={}
        new_df["Topsis Score"]=topsis
        topsis.sort(reverse=True)
        #Rank Determination based on the Topsis Score
        # Higher the Topsis Score Better the Rank
        rank_dict[topsis[0]]=1
        rank=2
        for val in range(1,len(topsis)):
            rank_dict[topsis[val]]=rank
            rank+=1
        rtp=[]
        for val in new_df["Topsis Score"]:
            rtp.append(rank_dict[val])
        new_df["Rank"]=rtp
        # Converting and Storing the Data-Frame to output csv file
        new_df.to_csv(outputFile,index=False)
    except FileNotFoundError:
        print("Input value is unable to find")
    except Invalid_Number_Of_Columns as ncol_error:
        print(ncol_error)
    except Unequal_Weights_And_Impacts as unequal_weight_and_impacts:
        print(unequal_weight_and_impacts)
    except Incorrect_Impact as incor_impact:
        print(incor_impact)
    except Invalid_Number_Of_Parameters as wrong_no_of_parameters:
        print(wrong_no_of_parameters)
    except ValueError:
        print("Value Present is Incorrect")



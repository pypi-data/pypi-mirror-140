import sys
import logging
import numpy as np
import pandas as pd
import os  

def topsis(file_name,weight,impact,result_file_name):
    logging.basicConfig(filename=result_file_name+"-log.txt", level=logging.INFO)
    try:
        df=pd.read_csv(file_name)
        model_name=list(df[df.columns[0]])
        data=df.iloc[:,1:]
        total_columns=data.shape[1]
        total_rows=data.shape[0]
        if total_columns<=2:
                logging.error('enter more than 3 columns in file')
                raise Exception("nter more than 3 columns in file")
                logging.shutdown() 
        for col in df.columns:
              if df[col].isnull().values.any():
                    logging.error(f"{col} contains null values")
                    raise Exception(f"{col} contains null values")
                    logging.shutdown()         
        for i in range(total_rows):
            for j in range(total_columns):
                if np.char.isnumeric(str(data.iloc[i,j]))==True:
                    logging.error('number are not numeric')
                    raise Exception("number are not numeric")
                    logging.shutdown() 
                    
        weight=weight.split(",")
        #print(weight)
        impact=impact.split(",")
        if(len(weight)!=total_columns):
                logging.error('enter weights properly')
                raise Exception("enter weight properly")
                logging.shutdown() 
            
        if(len(impact)!=total_columns):
                logging.error('enter impact properly')
                raise Exception("enter impact properly")
                logging.shutdown() 
       
        for i in impact:
            if i!="+" and i!="-":
                logging.error('impact must be positive or negative')
                raise Exception("impact must be positive or negative")
                logging.shutdown() 
                
       
        for i in range(total_columns):
            temp=0;
            for j in range(total_rows):
                temp=temp+data.iloc[j,i]**2
            temp=temp**0.5
            for j in range(total_rows):
                #print(data.iloc[j,i])
                data.iat[j,i]=(data.iloc[j,i]/temp)*int(weight[i])

        vj_positive=[]
        vj_negative=[]
        for i in range(total_columns):
            if impact[i]=="+":
                vj_positive.append(data.iloc[:,i].max())
                vj_negative.append(data.iloc[:,i].min())
            if impact[i]=="-":
                vj_positive.append(data.iloc[:,i].min())
                vj_negative.append(data.iloc[:,i].max())
        sj_positive=[]
        sj_negative=[]
        for i in range(total_rows):
            temp=0
            temp1=0
            for j in range(total_columns):
                temp=temp+(vj_positive[j]-data.iloc[i,j])**2
                temp1=temp1+(vj_negative[j]-data.iloc[i,j])**2
            sj_positive.append(temp**0.5)
            sj_negative.append(temp1**0.5)
        topsis_score=[]
        for i in range(len(sj_positive)):
            a=sj_negative[i]/(sj_negative[i]+sj_positive[i])
            topsis_score.append(a)
        arr=np.array(topsis_score)
        index=np.argsort(arr)[::-1]

        df["topsis_score"]=topsis_score
        topsis_score = pd.DataFrame(topsis_score)
        topsis_rank = topsis_score.rank(method='first',ascending=False)
        df["rank"]=topsis_rank
        df.to_csv(result_file_name,index=False)
    
    
    except IOError:
        logging.error('file path not found')
        print('file path not found')  
        logging.shutdown()        
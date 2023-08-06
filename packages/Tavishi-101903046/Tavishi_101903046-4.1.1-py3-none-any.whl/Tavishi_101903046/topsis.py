import sys
import pandas as pd
import numpy as np
import logging

def inDigit(x):
  try:
    return float(x)
  except ValueError:
        logging.error("Weights: Enter numeric values!!")
        raise Exception("Weights: Enter numeric values!!")
        logging.shutdown()    
def topsis(filename,weights,impacts,resultfile):
    logging.basicConfig(filename="101903046-log.txt", level=logging.INFO)
    try:
      df=pd.read_csv(filename)
      for col in df.columns:
        if df[col].isnull().values.any():
          logging.error(f"{col} contains null values")
          raise Exception(f"{col} contains null values")      
          logging.shutdown() 

      if len(df.columns)<3:
        logging.error("No of inappropriate columns, minimum 3 needed")
        raise Exception("No of inappropriate columns, minimum 3 needed")      
        logging.shutdown() 
      i=0
      weights = weights.split(",")
      impacts = impacts.split(",")
      data=df.iloc[:,1:]    
      for p in range(len(weights)):
        weights[p] = inDigit(weights[p])
      if data.shape[1] != data.select_dtypes(include=["float", 'int']).shape[1]:
        logging.error("Columns numst contain only numeric values")
        raise Exception("Columns numst contain only numeric values")
        logging.shutdown()

      if(len(weights)<len(data.columns)):
            logging.error("weights are less in number!!")
            raise Exception("weights are less in number!!")
            logging.shutdown()
      if(len(impacts)<len(data.columns)):
            logging.error("Impacts are less in number!!")
            raise Exception("Impacts are less in number!!")
            logging.shutdown()
      best_val = []
      worst_val = []
      for column in data.columns:
        sq = data[column].pow(2).sum()
        sq = np.sqrt(sq)
        data[column] = data[column]*weights[i]/sq
        if(impacts[i]=='+'):
          best_val.append(data[column].max())
          worst_val.append(data[column].min())
        elif(impacts[i]=='-'):
          best_val.append(data[column].min())
          worst_val.append(data[column].max())
        else:
          logging.error("Impacts: Invalid input enter only '+' or '-'")
          raise Exception("Impacts: Invalid input enter only '+' or '-'")
          logging.shutdown()
        i+=1
      euclid_best=0
      euclid_worst=0
      topsis_score=[]
      column = len(data.columns)
      row = len(data)
      for x in range(row):
        for y in range(column):
          euclid_best+=(data.iloc[x][y]-best_val[y])**2
          euclid_worst+=(data.iloc[x][y]-worst_val[y])**2
        euclid_worst = np.sqrt(euclid_worst)
        euclid_best = np.sqrt(euclid_best) + euclid_worst
        topsis_score.append(euclid_worst/euclid_best)
      data["Topsis_score"]=topsis_score  
      topsis_score = pd.DataFrame(topsis_score)
      topsis_rank = topsis_score.rank(method='first',ascending=False)
      data["Rank"]=topsis_rank
      # data.insert(column+2,"Rank",topsis_score,allow_duplicates=False)
      # print(dataset)
      data.to_csv(resultfile,index=False)  
    except IOError:
      logging.error("file not found!!")
      raise Exception("file not found!!")
      logging.shutdown()
 
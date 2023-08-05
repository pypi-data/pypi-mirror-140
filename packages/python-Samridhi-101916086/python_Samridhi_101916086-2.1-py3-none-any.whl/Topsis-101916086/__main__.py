import sys
import pandas as pd
import numpy as np
# logging.basicConfig(filename="101916086-log.txt", level=logging.INFO)
class topsis:
  def read_file(self):
      try:
        read = pd.read_excel (self.filename)
        read.to_csv ("101916086-data.csv", index = None,header=True)
        df=pd.read_csv("101916086-data.csv")
        for col in df.columns:
          if df[col].isnull().values.any():
            # logging.error(f"{col} contains null values")
            print(f"{col} contains null values")      
            # logging.shutdown() 

        if len(df.columns)<3:
          # logging.error("No of inappropriate columns, minimum 3 needed")
          print("No of inappropriate columns, minimum 3 needed")      
          # logging.shutdown() 
        return df
      except IOError:
        raise Exception("file not found!!")

  def inDigit(self,x):
    try:
      return float(x)
    except ValueError:
          # logging.error("Weights: Enter numeric values!!")
          raise Exception("Weights: Enter numeric values!!")
          # logging.shutdown()        

  def calculate(self):
    i=0
    self.weights = self.weights.split(",")
    self.impacts = self.impacts.split(",")
    dataset = self.read_file()
        
    for p in range(len(self.weights)):
      self.weights[p] = self.inDigit(self.weights[p])
    if(dataset.iloc[0][0]):
      data = pd.DataFrame(dataset.iloc[:,1:])
    else:
      data = dataset
    if data.shape[1] != data.select_dtypes(include=["float", 'int']).shape[1]:
      # logging.error("Columns numst contain only numeric values")
      raise Exception("Columns numst contain only numeric values")
      # logging.shutdown()

    if(len(self.weights)<len(data.columns)):
          # logging.error("weights are less in number!!")
          raise Exception("weights are less in number!!")
          # logging.shutdown()
    if(len(self.impacts)<len(data.columns)):
          # logging.error("Impacts are less in number!!")
          raise Exception("Impacts are less in number!!")
          # logging.shutdown()
    best_val = []
    worst_val = []
    for column in data.columns:
      sq = data[column].pow(2).sum()
      sq = np.sqrt(sq)
      data[column] = data[column]*self.weights[i]/sq
      if(self.impacts[i]=='+'):
        best_val.append(data[column].max())
        worst_val.append(data[column].min())
      elif(self.impacts[i]=='-'):
        best_val.append(data[column].min())
        worst_val.append(data[column].max())
      else:
        # logging.error("Impacts: Invalid input enter only '+' or '-'")
        raise Exception("Impacts: Invalid input enter only '+' or '-'")
        # logging.shutdown()
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
    dataset["Topsis_score"]=topsis_score  
    topsis_score = pd.DataFrame(topsis_score)
    topsis_score = topsis_score.rank(method='first',ascending=False)
    topsis_score.columns = ['Rank']
    dataset.insert(column+2,"Rank",topsis_score,allow_duplicates=False)
    # print(dataset)
    dataset.to_csv(self.resultfile,index=False)  


  def __init__ (self,filename,weights,impacts,resultfile):
    self.filename = filename
    self.weights = weights
    self.impacts = impacts
    self.resultfile=resultfile
    self.calculate()

def main(filename,weights,impacts,resultfile):
  t = topsis(filename,weights,impacts,resultfile)

if __name__ == '__main__':
    para=len(sys.argv)
    if para!=5:
        # logging.error("Invalid number of arguments,needed parameters: 4, in the order--(inputfile,weights,impacts,outputfile)")
        print("Invalid number of arguments,needed parameters: 4, in the order--(inputfile,weights,impacts,outputfile)")
        # logging.shutdown()     
    filename = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    resultfile=sys.argv[4]
    main(filename,weights,impacts,resultfile)
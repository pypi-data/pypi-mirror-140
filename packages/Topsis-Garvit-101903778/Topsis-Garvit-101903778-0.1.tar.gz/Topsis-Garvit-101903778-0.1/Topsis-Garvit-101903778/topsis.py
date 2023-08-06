from tabulate import tabulate
from os import path
import pandas as pd
import math
import sys

def topsis(fName,weight,impact,resultName):
  df = pd.read_csv(fName)
  df.dropna(inplace = True)
  dfNumeric = df.iloc[0:,1:].values
  matrix = pd.DataFrame(dfNumeric)
  sumOfSq = []

  for col in range(0,len(matrix.columns)):
    x = matrix.iloc[0:,[col]].values
    sum = 0
    for i in x :
      sum += (i*i)
    sumOfSq.append(math.sqrt(sum))
  j = 0
  while(j < len(matrix.columns)):
    for i in range(0,len(matrix)):
      matrix[j][i] /= sumOfSq[j]
    j+=1
  
  k = 0
  while(k<len(matrix.columns)):
    for i in range(0,len(matrix)):
      matrix[k][i] *= weight[k]
    k+=1
  
  bestV = []
  worstV = []
  for col in range(0,len(matrix.columns)):
    y = matrix.iloc[0:,[col]].values

    if impact[col] == '+':
      maxV = max(y)
      minV = min(y)
      bestV.append(maxV[0])
      worstV.append(minV[0])
    
    if impact[col] == '-':
      maxV = max(y)
      minV = min(y)
      bestV.append(minV[0])
      worstV.append(maxV[0])
  
  siPlus = []
  siMinus = []

  for row in range(0,len(matrix)):
    t = 0
    t1 = 0
    r = matrix.iloc[row,0:].values
    for v in range(0,len(r)):
      t += math.pow(r[v]-bestV[v],2)
      t1 += math.pow(r[v]-worstV[v],2)
    siPlus.append(math.sqrt(t))
    siMinus.append(math.sqrt(t1))
  
  Pi = []
  for row in range(0,len(matrix)):
    Pi.append(siMinus[row]/(siPlus[row]+siMinus[row]))
  
  rank = []
  sortedPi = sorted(Pi,reverse = True)
  for row in range(0,len(matrix)):
    for i in range(0,len(sortedPi)):
      if Pi[row] == sortedPi[i]:
        rank.append(i+1)
  
  column1 = df.iloc[:,[0]].values
  matrix.insert(0,df.columns[0],column1)
  matrix['Topsis Score'] = Pi
  matrix['Rank'] = rank

  newColNames = []
  for name in df.columns:
    newColNames.append(name)
  newColNames.append('Topsis Score')
  newColNames.append('Rank')
  matrix.columns = newColNames

  matrix.to_csv(resultName)
  print(tabulate(matrix,headers=matrix.columns))

def checkParameters():
  if len(sys.argv)==5:
    filename = sys.argv[1].lower()
    weights = sys.argv[2].split(",")
    for i in range(0,len(weights)):
      weights[i] = int(weights[i])
    
    impacts = sys.argv[3].split(",")
    resultFileName = sys.argv[-1].lower()
    if ".csv" not in resultFileName :
      print("Result File Name should contain .csv")
    if path.exists(filename):
      if len(weights)==len(impacts):
        topsis(filename,weights,impacts,resultFileName)
      else :
        print("INPUT ERROR!! Number of weights and impacts should be same.")
        return
    else :
      print("Check Input, INPUT FILE DOESNOT EXIST")
      return
  else :
    print("Required Number of arguments are not provided")
    print("Input Format : python <script_name> <input_filename> <weights> <impacts> <result_filename")
    return

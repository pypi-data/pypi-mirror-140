import sys
import math
import pandas as pd
import numpy as np

def main():
   if len(sys.argv) != 5:
      print('Incorrect number of parameters')
      exit(0)

   try:
      weights = list(map(float, sys.argv[2].split(',')))
      impacts = list(map(str, sys.argv[3].split(','))) 
   except:
      print('Separate weights and impacts with commas')
      exit(0)
         
   for ch in impacts:
      if ch not in ('+','-'):
         print('Incorrect impacts')
         exit(0)

   result = sys.argv[4]

   try:
      dataCSV = pd.read_csv(sys.argv[1])
   except:
      print('File not found')
      exit(0)
         
   if len(list(dataCSV.columns)) < 3:
      print('Less than 3 columns not allowed')
      exit(0)
         
   data = dataCSV.drop(['Fund Name'], axis = 1)
   (r,c) = data.shape

   if len(weights) != c or len(impacts) != c:
      print("Incorrect number of weights or impacts")
      exit(0)

   data = data.values.astype(float)
   totalW = np.sum(weights)

   rms = [0]*(c)
   for i in range(0,r):
      for j in range(0,c):
         rms[j] += (data[i][j] * data[i][j])

   for j in range(c):
      rms[j] = math.sqrt(rms[j])        
         
   for i in range(c):
      weights[i] /= totalW

   for i in range(r):
      for j in range(c):
         data[i][j] = (data[i][j] / rms[j]) * weights[j]

   maxData = np.amax(data, axis = 0) 
   minData = np.amin(data, axis = 0)

   for i in range(len(impacts)):
      if(impacts[i] == '-'):         
         temp = maxData[i]
         maxData[i] = minData[i]
         minData[i] = temp

   euclidPlus = []
   euclidMinus = []

   for i in range(r):
      sum = 0
      for j in range(c):
         sum += pow((data[i][j] - maxData[j]), 2)
      euclidPlus.append(float(pow(sum, 0.5)))

   for i in range(r):
      sum = 0
      for j in range(c):
         sum += pow((data[i][j] - minData[j]), 2)
      euclidMinus.append(float(pow(sum, 0.5)))

   performance = {}

   for i in range(r):
      performance[i + 1] = euclidMinus[i] / (euclidMinus[i] + euclidPlus[i])

   p = list(performance.values())
   pFinal = sorted(list(performance.values()), reverse = True)

   rank = {}

   for val in p:
      rank[(pFinal.index(val) + 1)] = val

   output = dataCSV
   output['Topsis Score'] = list(rank.values())
   output['Rank'] = list(rank.keys())

   res = pd.DataFrame(output)
   res.to_csv(result, index = False)

if __name__ == "__main__":
   main()
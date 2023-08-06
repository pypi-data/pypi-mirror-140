
import numpy as np
import pandas as pd
import sys
import warnings
import copy
if len(sys.argv)!=5:
  raise Exception("Input Parameters is not equal to 5")
  sys.exit()

try:
  with open(sys.argv[1]) as f:
    pass

except FileNotFoundError:
  raise Exception('Input File Not Found')
  sys.exit()

except:
  sys.exit()


filename = sys.argv[1]
df = pd.read_csv(filename)

if(len(df.columns)<3):
  raise Exception("Number of Columns is less than 3")
  sys.exit()



wt = sys.argv[2]
impact = sys.argv[3]
resFileName = sys.argv[4]
wtls = wt.split(',')

try:
  wtls = [float(x.strip()) for x in wtls]
except:
  raise Exception("Weights are not seperated by comma")
  sys.exit()

impls = impact.split(',')
try:
  impls = [x.strip() for x in impls]
except:
  raise Exception("Impactss are not seperated by comma")
  sys.exit()

if(len(wtls)!=len(impls) or (len(df.columns)-1)!=len(impls) or len(wtls)!=(len(df.columns)-1)):
  raise Exception("Number of weights, number of impacts and number of columns are not equal")
  sys.exit()
  


for i in range(0,len(impls)):
  if impls[i]=='+':
    impls[i]=1
  elif impls[i]=='-':
    impls[i]=-1
  else:
    raise Exception('Impact value is other than \'+\' or \'-\'')
    sys.exit()

numdf = df.iloc[:,1:]

try:
  numdf.iloc[:,1:].apply(lambda h:pd.to_numeric(h,errors='raise').notnull().all())
except:
  raise Exception("Values are non numeric")
  sys.exit()
  

s=[]
n=len(numdf.columns)
for i in range(0,n):
  s.append(sum((numdf.iloc[:,i]**2)))

s = [val**0.5 for val in s]


for i in range(0,len(numdf)):
  for j in range(0,len(numdf.columns)):
    numdf.iloc[i,j] = numdf.iloc[i,j]/s[j]



for i in range(0,len(numdf)):
  for j in range(0,len(numdf.columns)):
    numdf.iloc[i,j] = numdf.iloc[i,j]*wtls[j]


idbest = []
idworst = []
for i in range(0,len(impls)):
  if impls[i]==1:
    idbest.append(max(numdf.iloc[:,i]))
    idworst.append(min(numdf.iloc[:,i]))
  else:
    idbest.append(min(numdf.iloc[:,i]))
    idworst.append(max(numdf.iloc[:,i]))


dis1 = []
dis2 = []
for i in range(0,len(numdf)):
  d1=0
  d2=0
  for j in range(0,len(numdf.columns)):
    d1 = d1+((numdf.iloc[i,j]-idbest[j])**2)
    d2 = d2+((numdf.iloc[i,j]-idworst[j])**2)

  dis1.append((d1**0.5))
  dis2.append((d2**0.5))


perf = []
for i in range(0,len(dis1)):
  perf.append(dis2[i]/(dis1[i]+dis2[i]))

perfsorted = copy.deepcopy(perf)
perfsorted.sort(reverse = True)


rank = []
for i in range(0,len(perf)):
  rank.append(perfsorted.index(perf[i])+1)

df['Rank']=rank
df.to_csv(resFileName)



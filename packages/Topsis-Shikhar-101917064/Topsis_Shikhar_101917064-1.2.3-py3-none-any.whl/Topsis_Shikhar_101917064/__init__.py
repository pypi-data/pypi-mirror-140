import pandas as pd
import sys

def topsis(a,b,c):
  
  df1 = a
  if len(df1.columns)<3:
    print("ERROR : Very few columns in dataframe")
    exit()
  df = df1.iloc[:,1:]
  for i in df.columns:
    if not pd.api.types.is_numeric_dtype(df[i]):
      print("ERROR : Only numeric values should be present in dataframe!!")
      exit()

  for i in b:
    if not(i.isdigit() or i==','):
      print("ERROR: Weights must be separated by ','(comma)")
      exit()

  for i in c:
    if not(i=='+' or i==',' or i=='-'):
      print("ERROR : Impacts must be separated by ','(comma)")
      exit()
  
  # setting the weights and impacts
  weights = b.split(',')
  weights = [int(i) for i in weights]
  impacts = c.split(',')

  if len(weights)!=len(df.columns):
    print("ERROR : Number of weights and no. of columns(excluding 1st one) should be same")
    exit()
  if len(impacts)!=len(df.columns):
    print("ERROR : Numbber of impacts and no. of columns(excluding 1st one) should be same")
    exit()
    
  for i in impacts:
    if not(i=='+' or i=='-'):
      print("Impacts must be either +ve or -ve")  
      exit()

  #weighted normalization
  for i in range(len(df.columns)):
    total = 0
    for j in range(len(df)):
      total += df.iloc[j,i]*df.iloc[j,i]
    total = total**0.5
    for j in range(len(df)):
      df.iloc[j,i] = (df.iloc[j,i]/total)*weights[i]

  #find ideal best and ideal worst
  best = []
  worst = []
      
  for i in range(len(df.columns)):   
    col = df.iloc[:,i]
    if impacts[i] == '+':
      best.append(col.max())
      worst.append(col.min())
    else:
      best.append(col.min())
      worst.append(col.max())

  #Calculate Euclidean distance
  dist_pos = []   #distance positive
  dist_neg = []   #distance negative
      
  for i in range(len(df)):
    total1=0
    total2=0
    for j in range(len(df.columns)):
      total1 += (df.iloc[i,j] - best[j])**2
      total2 += (df.iloc[i,j] - worst[j])**2
    dist_pos.append(total1**0.5)
    dist_neg.append(total2**0.5)

  #calculate performance score
  score = []
  for i in range(len(dist_pos)):
    score.append(dist_neg[i]/(dist_neg[i]+dist_pos[i]))
  score = [round(i,3) for i in score]

  first = df1.columns[0]
  output_df = df1[[first]].copy()
  output_df["Topsis Score"]=score
  output_df['Rank'] = (output_df['Topsis Score'].rank(method='max', ascending=False))
  output_df = output_df.astype({"Rank": int})

  print(output_df)  #displaying


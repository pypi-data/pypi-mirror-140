import pandas as pd
import math
import sys
def claculation_topsis():
    df=pd.read_csv(sys.argv[1])
    temp = sys.argv[2]
    weight = list(temp.split(","))
    weight = [float(i) for i in weight]
    temp = sys.argv[3]
    impact = list(temp.split(","))
    df1=pd.DataFrame()
    ideal_best_value=list()
    ideal_worse_value=list()
    score=list()
    a=0
    for col in df.columns[1:]:
      df1=df[col]**2
      df[col]=df[col]/math.sqrt(df1.sum())
      df[col]=df[col]*(weight[a])
      if(impact[a]=='+'):
        ideal_best_value.append(df[col].max())
        ideal_worse_value.append(df[col].min())
      elif(impact[a]=='-'):
        ideal_best_value.append(df[col].min())
        ideal_worse_value.append(df[col].max())
      a+=1

    for i in df.index:
      df1=df.iloc[i,1:len(df)]
      temp1=(df1-ideal_best_value)**2
      ideal_best=math.sqrt(temp1.sum())
      temp2=(df1-ideal_worse_value)**2
      ideal_worse=math.sqrt(temp2.sum())
      score.append(ideal_worse/(ideal_best+ideal_worse))
    df['Topsis Score']=score
    df['Rank'] = df['Topsis Score'].rank(ascending=False)
    df = df.round(decimals=2)
    df.to_csv(sys.argv[4], index=False)
    print(df)


if __name__ == '__main__':
  claculation_topsis()


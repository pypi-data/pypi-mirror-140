import pandas as pd
import math as m
import sys

def main():
    if len(sys.argv)!=5 :
         raise Exception("Number of parameters are wrong.Please check the number of parameters.")
    if sys.argv[1].endswith(('.csv')):
         pass
    else:
         raise Exception("Type of the file must be .csv")
    filename=sys.argv[1]
    
    try:
            df=pd.read_csv(filename)
    except:
            print("No such file found")
            sys.exit()

    weights = sys.argv[2]
    impacts = sys.argv[3]
    result=sys.argv[4]
    
    for i in  impacts:
                
            if i =='+' or i=='-' or ',':
                pass
            else:
                raise Exception("Only + and - values are accepted")
            
                
    cnt=0            
    for i in  weights:
            if i ==',':
                cnt=cnt+1
    
    if cnt == 0:             
       raise Exception("Values should be seperated by commas")
       sys.exit()
       
       
    cnt=0            
    for i in  impacts:
            if i ==',':
                cnt=cnt+1
    
    if cnt == 0:             
       raise Exception("Values should be seperated by commas")
       sys.exit()
       
    topsis(df,weights,impacts,result)

def topsis(data, Weights, Impacts,result):
    

    dataset = data
    X = dataset.iloc[:, 1:].values
    X = X.astype(float)

    W = []
    impact = []
    for i in Weights:
      if i != ',': W.append(float(i))
    for i in Impacts:
      if i != ',': impact.append(i)

    a, b, c, d = 0, 0, 0, 0
    for i in range(len(X)):
      a += X[i][0] * X[i][0]
      b += X[i][1] * X[i][1]
      c += X[i][2] * X[i][2]
      d += X[i][3] * X[i][3]
    a = float(m.sqrt(a))
    b = float(m.sqrt(b))
    c = float(m.sqrt(c))
    d = float(m.sqrt(d))

    for i in range(len(X)):
      for j in range(len(X[0])):
        if j == 0: X[i][j] /= a
        elif j == 1: X[i][j] /= b
        elif j == 2: X[i][j] /= c
        elif j == 3: X[i][j] /= d

    for i in range(len(X)):
      for j in range(len(X[0])):
        if j == 0: X[i][j] *= W[0]
        elif j == 1: X[i][j] *= W[1]
        elif j == 2: X[i][j] *= W[2]
        elif j == 3: X[i][j] *= W[3]

    Vj_plus = []
    Vj_minus = []
    for j in range(len(X[0])):
      mn=1000
      mx=-1
      for i in range(len(X)):
        mn = min(mn, X[i][j])
        mx = max(mx, X[i][j])
      if (impact[j] == '+'):
        Vj_plus.append(mx)
        Vj_minus.append(mn)
      else:
        Vj_plus.append(mn)
        Vj_minus.append(mx)

    Sj_plus = []
    Sj_minus = []
    for i in range(len(X)):
      sum1, sum2 = 0, 0
      for j in range(len(X[0])):
        sum1 += (X[i][j] - Vj_plus[j]) ** 2
        sum2 += (X[i][j] - Vj_minus[j]) ** 2
      Sj_plus.append(m.sqrt(sum1))
      Sj_minus.append(m.sqrt(sum2))

    topsis_score = []
    for i in range(len(Sj_plus)):
      topsis_score.append(Sj_minus[i] / (Sj_plus[i] + Sj_minus[i]))

    dataset["Topsis Score"] = topsis_score
    dataset["Rank"] = dataset["Topsis Score"].rank(ascending= False) 
    dataset.sort_values("Topsis Score", inplace = True)
    dataset = dataset.sort_index(axis=0)
    dataset.to_csv(result,index=False)
    print(dataset)

if __name__ == "__main__":
    main()

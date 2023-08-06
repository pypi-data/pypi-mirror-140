import pandas as pd
import numpy as np
import topsispy as tp
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
            
    df.head()
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
    
    val=df[['P1','P2','P3','P4','P5']]
    arr=np.array(val)
    arr
    
    weights = list(map(float ,weights.split(',')))
    impacts = list(map(str ,impacts.split(',')))
    
    for i in range(0,len(impacts)):
        if impacts[i]=='+':
            impacts[i]=1
        elif impacts[i]=='-':
            impacts[i]=-1
    
    (row,c)=df.shape
    c=c-1
    if c<3:
            raise Exception("Insufficient number of columns.# or more required.")
    
    if len(weights) != c:
            raise Exception("Insufficient Weights")
    if len(impacts) != c:
            raise Exception("Insufficient Impacts")
    topsis_cal(df, weights, impacts, result, arr)


def calculate_topsis(df,arr,weights,impacts):
    topsis=tp.topsis(arr, weights, impacts)
    scores=topsis[1]
    (row,c)=df.shape
    
    a=scores.copy()
    a.sort()
    r=[]
    for i in scores:
        cnt=row
        for j in a:
            if j==i:
                r.append(cnt)
                break
            cnt=cnt-1
        
    
    column_values=["Rank"]
    
    rank_df = pd.DataFrame(data = r, 
                      columns = column_values)
    
    column_val=["Topsis Score"]
    
    score_df = pd.DataFrame(data = scores, 
                      columns = column_val)
    
    return rank_df,score_df

def topsis_cal(df,weights,impacts,result,arr):
    rank_df,score_df=calculate_topsis(df, arr, weights, impacts)
    res= pd.concat([df,score_df, rank_df], axis=1)
    
    res.to_csv(result,index=False)

if __name__ == "__main__":
    main()

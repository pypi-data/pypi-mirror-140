import csv
import sys
import numpy as np
import pandas as pd
import argparse 

#step:1 normalize the matrix and multiply with weights
def normalize(y,m,n,weights):    
    rms = np.zeros((n,1))    
    for i in range(n):        
        for j in range(m):            
            rms[i] += ((y[j,i])**2)            
        rms[i] = (rms[i])**(0.5)
            
    for i in range(n):        
        for j in range(m):            
            y[j,i] = (y[j,i]/rms[i])*(weights[i])
            
    return y


#step:2 find ideal values
def idealvals(x,m,n,impacts):    
    v_best = np.zeros((n,1))
    v_worst = np.zeros((n,1))
    
    for i in range(n):        
        if impacts[i] == '+':
            v_best[i] = max(x[:,i])
            v_worst[i] = min(x[:,i])
            
        elif impacts[i] == '-':
            v_worst[i] = max(x[:,i])
            v_best[i] = min(x[:,i])
            
        else:
            print("Invalid symbol(s) in Impacts vector")
            sys.exit(0)
            
    return v_best,v_worst


#step:3 find euclidean distance and performance score
def performance(x,m,n,v_best,v_worst):    
    s_best = np.zeros((m,1))
    s_worst = np.zeros((m,1))
    
    p = np.zeros((m,1))
    
    for j in range(m):        
        for i in range(n):            
            s_best[j] += (x[j,i] - v_best[i]) ** 2
            s_worst[j] += (x[j,i] - v_worst[i]) ** 2
            
        s_best[j] = (s_best[j]) ** (0.5)
        s_worst[j] = (s_worst[j]) ** (0.5)
        
        p[j] = s_worst[j] / (s_worst[j] + s_best[j])
        
    return p
  
    
#step:4 assign ranks to datapoints
def rank_df(p,m):    
    index = list( range(1, m+1) )
    df=pd.DataFrame(p,index=index,columns=['P-Score'])    
    df['Rank'] = df['P-Score'].rank(ascending=False).astype(int)    
    return df
   
    
    
    
def main():

    # parse command line arguments 
    parser = argparse.ArgumentParser(prog ='topsis',prefix_chars='/')
    parser.add_argument("InputDataFile", help="Enter the name of CSV file with .csv extention",type=str)
    parser.add_argument("Weights", help="Enter the weight vector comma separated" ,type=str)
    parser.add_argument("Impacts", help="Enter the impact vector comma separated",type=str)
    parser.add_argument("OutputDataFile", help="Enter the name of CSV file with .csv extention",type=str)

    args = parser.parse_args()
    args = vars(args)
    
    FILENAME = args['InputDataFile']
    WEIGHTS = args['Weights']
    IMPACTS = args['Impacts']
    OUTFILE = args['OutputDataFile']

    try:
        f = open(FILENAME, 'r')
       
    except IOError:
       print ("There was an error reading", FILENAME)
       sys.exit(0)

    data = np.array(list(csv.reader(f)))
    data = np.array(data[1:,1:],dtype=float)
    
    n = np.size(data,1)
    m = np.size(data,0)
    

    try:    
        WEIGHTS = [int(x) for x in WEIGHTS.replace(' ', '').split(',')];
  
    except ValueError:
        print ("Incorrect value(s) in Weight vector")
        sys.exit()
    
    if(len(WEIGHTS) != n):
        print("Incorrect input size for Weights vector")
        sys.exit(0)
    
    
    try:
        IMPACTS = IMPACTS.replace(' ', '').split(',')

    except ValueError:
        print ("Incorrect value(s) in Impacts vector")
        sys.exit(0)

    if(len(IMPACTS) != n):
        print("Incorrect input size for Impacts vector")
        sys.exit(0)    

    data = normalize(data,m,n,WEIGHTS)

    v_best,v_worst = idealvals(data,m,n,IMPACTS)

    p_score = performance(data,m,n,v_best,v_worst)
       
    ranked_df = rank_df(p_score,m)
    
    inputdataframe = pd.read_csv(FILENAME)
    inputdataframe.index = inputdataframe.index + 1
    
    result = pd.concat([inputdataframe, ranked_df], axis=1)
    
    result.to_csv(OUTFILE, mode='w', index=False, header=True)
    
    
# driver code    
if __name__ == "__main__":
    main()
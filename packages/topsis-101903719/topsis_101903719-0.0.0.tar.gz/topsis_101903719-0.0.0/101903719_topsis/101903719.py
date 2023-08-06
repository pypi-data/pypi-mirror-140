#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pandas as pd
import os
import sys
import numpy as np
def validate(impact,weights,df):
        size = len(df.columns.values)
        if size < 3:
            print("ERROR : Columns in your input file are less than 3")
            sys.exit()
        
        for i in impact:
            if(i != '+' and i != '-'):
                print("ERROR : Wrong values of impacts")
                sys.exit()
        
        a=len(weights)
        b=len(impact)
        if(a!=b):
            print("ERROR : Number of weights are not equal to the number of imapcts")
            sys.exit()
        
        
 
def findmaxandmin(df,size,impact):
        add = (df.max().values)[1:]
        sub = (df.min().values)[1:]
                  
        # if imapct is negative
                  
        for i in range(1, size):
            if impact[i-1] == '-':
                # swap the values
                
                temp=add[i-1]
                add[i-1]=sub[i-1]
                sub[i-1]=temp
        return add,sub
    


    

def main(): 
    
     

        if not os.path.isfile(sys.argv[1]):
            print("ERROR :" "Invalid input")
            sys.exit()

    
        elif ".csv" != (os.path.splitext(sys.argv[1]))[1]:
            print("ERROR :Please enter a valid csv file")
            sys.exit()

              
        
              
        else:
            output, df = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[1])
            impact = sys.argv[3].split(',')
            weights = [int(i) for i in sys.argv[2].split(',')]
            validate(impact,weights,df)
        

        
        

        size = len(df.columns.values)
        for i in range(1, size):
            pd.to_numeric(output.iloc[:, i], errors='coerce')
            output.iloc[:, i].fillna(
                (output.iloc[:, i].mean()), inplace=True)

        
        

        
        

        if ".csv" != (os.path.splitext(sys.argv[4]))[1]:
            print("ERROR :Please enter a valid csv file")
            sys.exit()
        if os.path.isfile(sys.argv[4]):
            os.remove(sys.argv[4])
        
        
        count=-1
        for (columnName, columnData) in df.iteritems():
            count=count+1
            if(count==0):
                continue
            len1 = df.shape[0]
            a=0
            for i in range(0,len1):
                a=a+((df[columnName][i])**2)
            a=a**0.5
            df1=df[columnName]/a
   
    
            df[columnName]=df1.copy(deep=True)
                  
            
                  
        # finding maximum and minimum values in a column
        add,sub=findmaxandmin(df,size,impact)          
        
               
                
        score = []
        
        length = df.shape[0]
        for i in range(0,length):
            a1=0
            a2=0
            idx=1
            while(idx<size):
                a1 = a1 + (add[idx-1] - df.iloc[i, idx])**2
                a2 = a2 + (sub[idx-1] - df.iloc[i, idx])**2
                idx=idx+1
                
            a1=a1**0.5
            a2=a2**0.5
            
            
            score.append(a2/(a1 + a2))
            
       
    

            
        output['Topsis Score'] = score
    
        
        output['Rank'] = (output['Topsis Score'].rank(method='max', ascending=0))
        output = output.astype({"Rank": int})
        output.to_csv(sys.argv[4], index=False)

        

if __name__ == "__main__":
    main()
    


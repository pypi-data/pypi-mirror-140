#!/usr/bin/env python
# coding: utf-8

# In[47]:


"""
Name - Harshit Verma
Roll Number - 101803398
Group - 3CO16
"""
import numpy as np
import pandas as pd
import os
import sys

def topsis():
    try:
        data = pd.read_csv(sys.argv[1])
        # data = pd.read_csv("101803398-data.csv")
    except:
        # input file not found in cwd
            print("Input file not found")
    else:
        col = list(data.columns)
        if(len(col) < 3):
            print("There are less than 3 columns in input file")
            exit(0)

        # Checks for weight
        weight = sys.argv[2]
        # weight = "5,3,2,1,2"
        weight_list = weight.split(',')

        if(len(weight_list) != (len(col) - 1)):
            print("weights dosen't match input data")
            exit(0)
        for w in weight_list:
            if(str.isdigit(w) == False):
                print("weights contain non numeric value")
                exit(0)

        weight_list = [int(w) for w in weight_list]


        # Checks for impacts
        impact = sys.argv[3]
        # impact = "+,+,-,+,-"
        impact_list = impact.split(',')

        if(len(impact_list) != (len(col) - 1)):
            print("impact dosen't match input data")
            exit(0)
        for w in impact_list:
            if(w not in ['+','-']):
                print("impact contains character other than '+' or '-'")
                exit(0)


        df = data.copy()
        df[col[1:]] = df[col[1:]].apply(pd.to_numeric, errors='coerce')
            # normalize data
        for i in range(1,len(col)):
            val=0
            for j in range(len(df)):
                val+=df.iloc[j,i]**2
            val**=0.5
            for j in range(len(df)):
                df.iat[j,i]=(df.iloc[j,i]/val)*weight_list[i-1]
        # Introduce impacts
        ncol=len(df.columns.values)
        positive_values=(df.max().values)[1:]
        negetive_values=(df.min().values)[1:]
        for i in range(1,ncol):
            if impact_list[i-1]=='-':
                # swap impacts 
                positive_values[i-1],negetive_values[i-1]=negetive_values[i-1],positive_values[i-1]
        
        # Topsis score and rank
        score =[]
        for i in range(len(df)):
            pos = 0
            neg = 0
            for j in range(1,len(col)):
                pos+=(positive_values[j-1]-df.iloc[i,j])**2
                neg+=(negetive_values[j-1]-df.iloc[i,j])**2
            pos = pos **0.5
            neg = neg ** 0.5

            score.append(neg/(pos+neg))

        df['Topsis Score'] = score

        # calculating rank accordingly
        df['Rank']=(df['Topsis Score'].rank(method='max',ascending=False))
        df=df.astype({"Rank":int})
        try:
            if((os.path.splitext(sys.argv[4]))[1]!=".csv"):
                print("Output file name not valid")
                exit(0)
            
            if(os.path.isfile(sys.argv[4])):
                os.remove(sys.argv[4])
            df.to_csv(sys.argv[4],index=False)
        except:
            print("Drive not accessable to write output file")


if __name__ == "__main__":
    topsis()
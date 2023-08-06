# -*- coding: utf-8 -*-
"""101917185.ipynb

Original file is located at
    https://colab.research.google.com/drive/1-1jNX3lFdPI8MkVEAGyJ-WQSQpE_eeh6
"""

import numpy as np
import pandas as pd

class MyTopsis:
    def __init__(self, input_file, weight, impact, out_file):
        self.input_file = input_file
        self.weight = weight
        self.impact = impact
        self.out_file = out_file

    def calculate:
        # Reading files
        dataset = pd.read_excel(input_file)
        df = dataset.iloc[:,1:].copy()
        # print(df)

        # setting the weights and impacts
        weights = weight
        choose = impact.split() 

        # Function to normalize the values
        def Normalization(df,weights):
            for i in range(df.shape[1]):
                total_sq_sum = 0
                
                for j in list(df.iloc[:,i]):
                    total_sq_sum += j**2
                deno = total_sq_sum**0.5
                
                for ind,k in enumerate(list(df.iloc[:,i])):
                    df.iloc[ind,i] = k*weights[i]/deno

        # function for calculating ideal best and ideal worst
        def calcIdeal(df,choose):
            ideal_best = []
            ideal_worst = []
            
            for i in range(df.shape[1]):
                if choose[i] == '+':
                    ideal_best.append(df.max()[i])
                    ideal_worst.append(df.min()[i])
                else:
                    ideal_best.append(df.min()[i])
                    ideal_worst.append(df.max()[i])
                    
            return ideal_best,ideal_worst

        # function for calculating topsis score
        # Here, I am using inbuilt function for calculating euclidean distance, provided in the numpy library
        # for custom, you can write it in the following way:
        # dist_pos.append(np.sqrt(sum((df.iloc[i,:].values-np.array(ideal_best))**2)))
        # dist_neg.append(np.sqrt(sum((df.iloc[i,:].values-np.array(ideal_worst))**2)))


        def topsisScore(df,ideal_best,ideal_worst):
            
            dist_pos = []
            dist_neg = []
            for i in range(df.shape[0]):
                    dist_pos.append(np.linalg.norm(df.iloc[i,:].values-ideal_best))
                    dist_neg.append(np.linalg.norm(df.iloc[i,:].values-ideal_worst))

            score = []
            for i in range(len(dist_pos)):
                score.append(dist_neg[i]/(dist_pos[i]+dist_neg[i]))
            
            return score

        # Calling the normalization function
        Normalization(df,weights)
        # print(df)

        # Calling the calcIdeal function
        ideal_best,ideal_worst = calcIdeal(df,choose)
        # print(ideal_best)
        # print(ideal_worst)

        # Calling the topsis score generator function
        score = topsisScore(df,ideal_best,ideal_worst)
        # print(score)

        # Adding the rank and score columns in the original dataset
        dataset['Topsis Score'] = score
        dataset['Rank'] = (dataset['Topsis Score'].rank(method='max', ascending=False))
        dataset = dataset.astype({"Rank": int})

        dataset.to_csv(out_file)

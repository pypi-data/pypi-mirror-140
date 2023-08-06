""" 
Dated - 27/02/2022
Name  - Rahul Goyal
Roll No - 101917152
Batch - CSE6
"""

import sys
import os
import pandas as pd
import math
import numpy as np
import csv

def topsis(file_name, weight, impact, output_file_name):

    try:
        # Fetch Labels
        df = pd.read_csv(file_name)
        list_of_column_names = list(df.columns)
        list_of_column_names.append('Topsis Score')
        list_of_column_names.append('Rank')
        # print(list_of_column_names)


        data = pd.read_csv(file_name).iloc[:,1:].values.tolist()
        # print(data)
        rows = len(data)
        columns = len(data[0])
        if columns<3:
            raise Exception("Insufficient number of columns")
        root_mean_square = [0]*(columns)
        
        # 1. Calculate Root Mean Square of each column
        for j in range(columns):
            for i in range(rows):
                root_mean_square[j] = root_mean_square[j] + (data[i][j])**2
            root_mean_square[j] = (root_mean_square[j])**(1/2)
        
        # print(root_mean_square)

        # 2. Vector Normalisation (divide each data entry by rms)
        normalised_data = list()
        for i in range(rows):
            l = list()
            for j in range(columns):
                l.append(data[i][j]/root_mean_square[j])
            normalised_data.append(l)
        
        
        # 3. Convert weights i.e 1/5 = 0.2 that would be multiplied by each row of 1's column
        split_weights = list(map(int, weight.strip().split(',')))
        if len(split_weights)!= columns:
            raise Exception("Length must be equal to the no of colns in the data.")
        
        for i in split_weights:
            if i<0:
                raise Exception("must be +")
        
        weights = list()
        
        for i in range(len(split_weights)):
            weights.append(split_weights[i]/sum(split_weights))
            
        if len(weights)!= columns:
            raise Exception("Length must be equal to the no of colns in the data.")
            

        # 4. Split impacts
        impacts = impact.strip().split(',')
        for i in impacts:
            if i not in ['+','-']:
                raise Exception("'+' or '-' signs only")
        
        # 5. Multiply weights with Data
        for j in range(len(data[0])):
            for i in range(len(data)):
                normalised_data[i][j] = normalised_data[i][j] * weights[j]
        

        # Transpose the data
        def transpose_data(normalised_data):
            t = list()
            for j in range(len(normalised_data[0])):
                l = list()
                for i in range(len(normalised_data)):
                    l.append(normalised_data[i][j])
                t.append(l)
            return t
                
        transpose = transpose_data(normalised_data)
        

        # Calculate the Ideal best and worst values based on impacts
        ideal_best = list()    # Vj+
        ideal_worst = list()   # Vj-

        for i in range(len(transpose)):
            if impacts[i] == '+':
                ideal_best.append(max(transpose[i]))
                ideal_worst.append(min(transpose[i]))
            if impacts[i] == '-':
                ideal_worst.append(max(transpose[i]))
                ideal_best.append(min(transpose[i]))
        


        # Calculate Performance score by calculating euclidean distance
        performance_score = list()
        for i in range(len(normalised_data)):
            euclidean_pos = 0   # Si+
            euclidean_neg = 0   # Si-
            for j in range(len(normalised_data[0])):
                euclidean_pos = euclidean_pos + (normalised_data[i][j] - ideal_best[j])**2
                euclidean_neg = euclidean_neg + (normalised_data[i][j] - ideal_worst[j])**2
            euclidean_pos = euclidean_pos**0.5
            euclidean_neg = euclidean_neg**0.5
            performance = euclidean_neg/(euclidean_neg+euclidean_pos)
            performance_score.append(performance)

        ranks = sorted(list(range(1,len(performance_score)+1)))
        pt = sorted(performance_score,reverse = True)
        
        perform = list()
        
        for i in performance_score:
            perform.append([i,ranks[pt.index(i)]])
        
        # print(perform)
        labels = {'row_no':['Score', 'Rank']}
        for i in range(len(perform)):
            labels[i] = perform[i]
        # for score,rank in labels.items():
            # print(score,rank)

        for i in range(rows):
            data[i].append(perform[i][0])
            data[i].append(perform[i][1])
        
        # print(data)
        final_data = [list_of_column_names]
        for i in range(rows):
            final_data.append(data[i])
        # print(final_data)
        with open(output_file_name,"w+") as my_csv:
            csvWriter = csv.writer(my_csv,delimiter=',')
            csvWriter.writerows(final_data)
    except:
        raise Exception("File not Found")

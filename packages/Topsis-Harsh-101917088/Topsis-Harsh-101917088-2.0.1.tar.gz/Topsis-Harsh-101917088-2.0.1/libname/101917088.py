# HARSH KASHYAP
# 101917088
# Thapar Institute Of Engineering and Technology
# CSE4

import sys
import numpy as np
import pandas as pd
import math
import copy


#Removing Print Statements.
# Convention - Print statements don't look good in library files

#print("From Harsh Kashyap\n")
#Checking if length of arguments passed is 5 or not
n = len(sys.argv)
#Proceed only if length is 5
if n == 5:
#First argumrnt should be a file
    if sys.argv[1] == "101917088-data.csv":
        try:
            file=sys.argv[1]
            #Read the file
            dataFile = pd.read_csv(file)
            #Create a deep copy
            finalData = copy.deepcopy(dataFile)
        except:
            print('File not Found! Please give a right file.')
            #Exit if file not found
            sys.exit()
        #No of properties greater than equal to 3
        if dataFile.shape[1] >= 3:
            for col in dataFile.columns[1:]:
                try:
                #Convert from first column to numeric
                    pd.to_numeric(dataFile[col])
                except:
                    print("Some columns are not numeric. Please enter right no. of columns")
                    
            #Seperate weights
            we = list(sys.argv[2].split(','))
            #Seperate positive or negative (good or bad)
            I = list(sys.argv[3].split(','))
            #Append weights
            w = []
            for i in we:
                w.append(float(i))
                
            #Length of weight and class should be equal to no. of properties
            if dataFile.shape[1]-1 == len(w) and dataFile.shape[1]-1 == len(I):
                list1 = []
                for col in dataFile.columns[1:]:
                    num = 0
                    for row in dataFile[col]:
                        num = num + row * row
                    #Normalising the properties
                    list1.append(math.sqrt(num))
                k = 1
                for i in range(dataFile.shape[0]):
                    for j in range(1, dataFile.shape[1]):
                        dataFile.iloc[i, j] = dataFile.iloc[i, j] / list1[j - 1]
                for i in range(dataFile.shape[0]):
                    for j in range(1, dataFile.shape[1]):
                        dataFile.iloc[i, j] = dataFile.iloc[i, j] * w[j - 1]
                        
                #Best feature Si+
                best = []
                #Worst feature Si-
                worst = []
                k = 0
                #Finding the best and worst feature
                for col in dataFile.columns[1:]:
                    #Min value best if feature is negative
                    if I[k] == '-':
                        best.append(dataFile[col].min())
                        worst.append(dataFile[col].max())
                    #Max value best if feature is negative
                    elif I[k] == '+':
                        best.append(dataFile[col].max())
                        worst.append(dataFile[col].min())
                    #Feature should be either positive or negative
                    else:
                        print("Impacts must be either +ve or -ve. Please give correct output")
                        sys.exit()
                    k = k + 1
                    
                #Finding the best and worst feature
                E_best = []
                E_worst = []
                
                
                #Finding distnace of all feature drom best and worst
                for i in range(dataFile.shape[0]):
                    square_Best = 0
                    square_Worst = 0
                    diff = 0
                    diff_best = 0
                    diff_worst = 0
                    for j in range(1, dataFile.shape[1]):
                        diff = dataFile.iloc[i, j] - best[j-1]
                        diff_best = diff * diff
                        diff = dataFile.iloc[i, j] - worst[j - 1]
                        diff_worst = diff * diff
                        square_Best = square_Best + diff_best
                        square_Worst = square_Worst + diff_worst
                        
                    #Finding ranking of all feature and appending it on the same basis
                    E_best.append(math.sqrt(square_Best))
                    E_worst.append(math.sqrt(square_Worst))
                P_score = []
                #Calculate TOPSIS rank
                for i in range(dataFile.shape[0]):
                    P_score.append(E_worst[i] / (E_worst[i] + E_best[i]))
                finalData['Topsis Score'] = P_score
                #Arrage in descending order
                finalData['Rank'] = finalData['Topsis Score'].rank(ascending=False)
                #Output file should be in form .csv
                if not(sys.argv[4].endswith('.csv')):
                    print('Incorrect file type, csv files allowed.')
                    sys.exit()
                #file created succesfully.
                else:
                    finalData.to_csv(sys.argv[4])
                    print("Output file generated created.")
            else:
                print("Number of weights, number of features or number of columns are not same. Please give right numbers.")
                print("Impacts and weights must be separated by ‘,’ ")
                sys.exit()
        #Error message for  more than 3 columns.
        else:
            print("Input file doesn't have more than 3 columns.")
            sys.exit()
        #Error message for wrong file name.
    else:
        print("File not found. Give correct file")
        sys.exit()
            #Error message for wrong argments.
else:
    print("Arguments passed are not equal to 4. Give right no. of arguments")


# HARSH KASHYAP
# 101917088
# Thapar Institute Of Engineering and Technology
# CSE4


#Thank You

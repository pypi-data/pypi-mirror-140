# # Version of Module
# __version__ = "1.0.0"


# Name:       Aashish Bansal


import numpy as np
import pandas as pd
import scipy.stats as ss


def topsis(input_filename, weights, impacts):
    try:
        input_file = pd.read_csv(input_filename)
        if(len(input_file.columns) < 3):
            print("Error: Number of columns provided in csv are less than 3.")
            exit()
        
        weights = [float(i) for i in weights.split(",")]
        if(len(weights) != (len(input_file.columns)-1)):
            print("Error: Number of weights provided are not equal to the number of numerical columns.")
            exit()
        
        impacts = impacts.split(",")
        if(len(impacts) != (len(input_file.columns)-1)):
            print("Error: Number of impacts provided are not equal to the number of numerical columns.")
            exit()
        for i in impacts:
            if(i!="+" and i!="-"):
                print("Error: Impacts provided are different from '+' and '-'.")
                exit()
    except Exception as ex:
        print(ex)
        exit()

    input_file = pd.read_csv(input_filename, keep_default_na=False)
    temp_input_file = input_file.iloc[:,1:]
    droprows = []
    for i in range(len(temp_input_file.index)):
        for j in range(len(temp_input_file.columns)):
            try:
                check = float(temp_input_file.iloc[i,j])
            except:
                droprows.append(i)
                break
    for i in droprows:
        temp_input_file.drop(temp_input_file.index[i], inplace=True)
    # print(temp_input_file)

    for i in range(len(temp_input_file.columns)):
        square_sum = sum(temp_input_file.iloc[:,i]**2)
        sum_root = square_sum**0.5
        temp_input_file.iloc[:,i] = temp_input_file.iloc[:,i]/sum_root

    # print(temp_input_file)
    for i in range(len(temp_input_file.index)):
        temp_input_file.iloc[i,:] = np.multiply(temp_input_file.iloc[i,:], weights)
    # print(temp_input_file)

    vplus = []
    vminus = []
    for i in range(len(temp_input_file.columns)):
        if(impacts[i] == "+"):
            vplus.append(max(temp_input_file.iloc[:,i]))
            vminus.append(min(temp_input_file.iloc[:,i]))
        else:
            vplus.append(min(temp_input_file.iloc[:,i]))
            vminus.append(max(temp_input_file.iloc[:,i]))

    # print(impacts)
    # print(temp_input_file)
    # print(vplus)
    # print(vminus)
    splus = []
    sminus = []
    for i in range(len(temp_input_file.index)):
        splus_temp = sum((np.subtract(temp_input_file.iloc[i,:], vplus))**2)
        splus_temp = splus_temp**0.5
        splus.append(splus_temp)
        sminus_temp = sum((np.subtract(temp_input_file.iloc[i,:], vminus))**2)
        sminus_temp = sminus_temp**0.5
        sminus.append(sminus_temp)
    # print(splus)
    # print(sminus)
    performance_score = []
    for i in range(len(splus)):
        performance_score.append((sminus[i])/(splus[i]+sminus[i]))
    # print(performance_score)
    rank = ss.rankdata(performance_score)
    rank = [int(i) for i in rank]
    # print(rank)
    # print(input_file)
    output_file = input_file
    output_file["Topsis Score"] = performance_score
    output_file["Rank"] = rank
    print(output_file)


    





# Name:       Aashish Bansal
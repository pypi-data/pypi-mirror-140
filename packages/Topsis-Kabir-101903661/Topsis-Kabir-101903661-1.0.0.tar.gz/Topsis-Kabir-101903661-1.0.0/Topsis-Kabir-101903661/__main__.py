#logging import
from cmath import log
from configparser import RawConfigParser
import logging
import re
#file reading import 
import sys
#general import
import pandas as pd
import numpy as np
import os


#topsis algorithm
def topsis(output, data, weights, impacts):
    ideal = []
    vector_normalization = pow(data.loc[:],2).sum()
    vector_normalization = vector_normalization.apply(lambda x: pow(x,0.5))
    #eucledian distance
    euc_dist_pos = []
    euc_dist_neg = []

    #normalized data
    for i in data.loc[:] :
        data[i] = data[i].apply(lambda x :x/vector_normalization[i])
    
    #to mulitply by weight
    k=0
    for i in data.loc[:]:
        data[i] = data[i].apply(lambda x : x * float(weights[k]))
        k+=1

    #finding ideal best and ideal worst
    j=0
    for i in data.loc[:]:
        if(impacts[j] == '+'):
            ideal.append([data[i].max() , data[i].min()])
        else:
            ideal.append([data[i].min() , data[i].max()])
        j+=1

    data_p = data
    data_n = data
    m=0
    for i in data_p.loc[:]:
        data_p[i] = data_p[i].apply(lambda x : pow(x-ideal[m][0],2))
        m+=1
    n=0
    for i in data_n.loc[:]:
        data_n[i] = data_n[i].apply(lambda x : pow(x-ideal[n][1],2))
        n+=1
    
    data['sum_p'] = pow(data_p.sum(axis=1),0.5)
    data['sum_n'] = pow(data_n.sum(axis = 1),0.5)
    data['sum'] = data[['sum_p','sum_n']].sum(axis=1)

    output["performance"] = data["sum_n"].divide(data["sum"])
    output["rank"] = output["performance"].rank(ascending=False)

    # saving the dataframe
    output.to_csv('101903661-result.csv')
    data.to_csv('101903661-data.csv')

#initial checkups
def main():
    #initializes a log file in append mode
    logging.basicConfig(
        filename='log.txt', 
        filemode='a',
        format='File: 101903661-1.py %(asctime)s %(levelname)s-%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    #checking if the input file argument is correct
    try:
        file = sys.argv[1]
    except:
        logging.error("Arguments insufficient")
        exit()

    #checking number of arguments
    if(len(sys.argv) != 4):
        logging.error("Incorrect number of arguments")
    
    #checking input file extension
    if (os.path.splitext(file)[1] != ".csv"):
        logging.error("Wrong input file")
        exit()

    if(type(sys.argv[2]) != str or type(sys.argv[3]) != str):
        logging.error("Wrong impacts and weights type")
        exit()
    #obtaining weights and impacts    
    weights = sys.argv[2].split(",")
    impacts = sys.argv[3].split(",")

    #checking if weights have char other than + or  -    
    if (weights in ['+','-']) :
        logging.error("Input can only contain + or -")
        exit()

    #reading file
    output = pd.read_csv(file)
    output = output.drop(output.columns[0], axis = 1)
    data = output.drop(output.columns[0],axis = 1)

    #checking the number of columns
    if((len(weights)!= data.shape[1]) or (len(impacts) != data.shape[1])):
        logging.error("Number of columns are not the same for impacts, weights and input file data")
        exit()

    if(data.applymap(lambda x: isinstance(x, (int, float))).all(axis = None) == False):
        logging.error("The data columns have a non numeric value")
        exit()
    
    topsis(output, data, weights, impacts)


if __name__ == "__main__":
    main()

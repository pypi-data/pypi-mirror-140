import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.filterwarnings("ignore")
from itertools import chain
from sqlalchemy import null
import logging
class Topsis:
    def lgExc(msg):
        logging.error(msg)
        raise Exception(msg)   
    def evaluate(self, df, outputFile, weights, impacts):
        v_max = []# for ideal best
        v_min = []# for ideal worst
        i = 0
        for col in df.columns[1:]:
            sq_sum=0   
            for index in df.index:
                sq_sum += df[col][index]**2
            for index in df.index:
                df[col][index] /= sq_sum
                df[col][index] *= pd.to_numeric(weights[i])
            if(impacts[i] == "-"):
                v_max.append(min(df[col]))
                v_min.append(max(df[col]))
            elif (impacts[i] == "+"):
                v_max.append(max(df[col]))
                v_min.append(min(df[col]))
            i+=1
        df["S_MAX"] = null()
        df["S_MIN"] = null()
        for index in df.index:
            s_mx, s_mn, i=0, 0, 0
            for col in df.columns[1:-3]:
                s_mx += (v_max[i] - df[col][index])**2
                s_mn += (v_min[i] - df[col][index])**2
                i=i+1
            s_mx = s_mx**0.5
            s_mn = s_mn**0.5
            df["S_MAX"][index] = s_mx
            df["S_MIN"][index] = s_mn
            df["TOPSIS_SCORE"] = null()
        for index in df.index:
            df["TOPSIS_SCORE"][index] = df["S_MIN"][index]/(df["S_MAX"][index] + df["S_MIN"][index])
        df.drop(columns=["S_MAX","S_MIN"], axis=0, inplace=True)   
        df['Rank'] = df["TOPSIS_SCORE"].rank(axis=0, ascending=False)
        for col in df.columns[1:]:
            df[col] = df[col]    
        df.to_csv(f'./{outputFile}', index=False)
def main():  
    eva = Topsis()
    logging.basicConfig(filename="101903438-LOGS.logs", level=logging.DEBUG)  
    if len(sys.argv) != 5:
        eva.lgExcp(f"5 arguments expected, {len(sys.argv)} received.\nCorrect format: python <program.py> <inputfilename.csv> <weights> <impacts> <outputfilename>")
    inputFile = sys.argv[1]
    # file = []
    # for (root,dirs,files) in os.walk('.'):
    #     file.append(files)
    # file = list(chain.from_iterable(file))
    # if(sys.argv[1] not in file):
    #     eva.lgExcp(f'No file with that name ({sys.argv[1]}) found in the current directory. Please correct the input and try again.')
    df = pd.read_csv(inputFile)
    if " " in sys.argv[2]:
       eva.lgExcp("Weights must only be separated by ',' and not by spaces.")
    weights = sys.argv[2].split(',')
    if " " in sys.argv[3]:
        eva.lgExcp("Impacts must only be separated by ',' and not by spaces.")
    impacts = sys.argv[3].split(',')
    for i in impacts:
        if i not in ["+","-"]:
            eva.lgExcp("Impacts must be either '+' or '-'.")
    if(len(df.columns) < 3):
        eva.lgExcp(f"Too few columns in input file, atleast 3 columns expected, received {len(df.columns)}.")
    if(len(weights) != len(impacts)):
        eva.lgExcp("Number of weights and impacts specified should be equal.")
    if(len(df.columns) - 1) != len(weights):
        eva.lgExcp("Weights or impacts not specified for all numeric columns.")
    if(type(df[df.columns[1:][0]][0]) not in [np.float64, np.float32, np.int64, np.int32]):
        eva.lgExcp("Non numeric column types found, correct the input file.")
    outputFile = sys.argv[4]

    eva.evaluate(df, outputFile, weights, impacts)     
if __name__ == '__main__':
    main()
        
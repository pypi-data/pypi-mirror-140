import sys
import numpy as np
import pandas as pd

#py 101903371.py 101903371-data.csv 1,1,1,2,2 +,-,+,-,+ 101903371-result.csv

def topsis(filename,weights,impacts,output_filename):

    #Check if input file is csv
    if filename.split(".")[-1]!="csv":
     	sys.exit("Error: Please enter a valid input csv file path.")


    #Check if output file is csv
    if output_filename.split(".")[-1]!="csv":
     	sys.exit("Error: Please enter a valid output csv file path.")


    try:

        #read data
        df = pd.read_csv(filename)


        #Check for all numeric values
        num_data = df.iloc[:,1:].values.tolist()
        if (np.isnan(num_data).any()==True):
            sys.exit("Error: From 2nd to last columns must contain numeric values only.")


        #Checking that number of columns is not less than 3
        if len(df.columns)<3:
             sys.exit("Error: Input file must contain three or more columns.")


        #Number of rows and columns
        ncols=df.iloc[:,1:].shape[1]
        nrows=df.iloc[:,1:].shape[0]


        #Checking that weights are correctly input
        # weights=list(map(int,weights_csv.strip().split(',')))
        # if len(weights)!=ncols:
        #     sys.exit("Error: Number of weights should be equal to number of columns.")
        #
        #
        # #Checking that impacts are correctly input
        # impacts=impacts_csv.strip().split(',')
        # if len(impacts)!=ncols:
        #     sys.exit("Error: Number of impacts should be equal to number of columns.")
        for i in impacts:
            if i not in ['+','-']:
                sys.exit("Error: Impacts should contain '+' or '-' signs only ")


        #Fetch column names
        columns_list = list(df.columns)
        columns_list.append('Topsis Score')
        columns_list.append('Rank')


        #Extract values from dataframe to work with into numpy array
        data=df.iloc[:,1:].values.tolist()


        #Calculate Root Mean Square for each column
        rms=[0]*ncols

        for j in range(ncols):
            for i in range(nrows):
                rms[j] = rms[j] + (data[i][j])**2
            rms[j] =  rms[j]**(1/2)


        #Normalisation by dividing each entry by rms value
        for i in range(nrows):
            for j in range(ncols):
                data[i][j]=data[i][j]/rms[j]


        #Multiply weights with data
        for j in range(ncols):
            for i in range(nrows):
                data[i][j]=data[i][j]*weights[j]


        #Transpose data in numpy array: data
        t_data=[]
        for j in range(ncols):
            temp1=[]
            for i in range(nrows):
                temp1.append(data[i][j])
            t_data.append(temp1)


        #Calculate ideal_best and ideal_worst
        ideal_best = []
        ideal_worst = []
        for i in range(len(t_data)):
            if impacts[i] == "+":
                ideal_best.append(max(t_data[i]))
                ideal_worst.append(min(t_data[i]))
            if impacts[i] == "-":
                ideal_best.append(min(t_data[i]))
                ideal_worst.append(max(t_data[i]))


        #Calculate euclidean distance from ideal best and ideal worst and Calculate performance score
        score_list=[]
        for i in range(nrows):
            ed_pos_ib=0 #Ideal Best
            ed_neg_iw=0 #Ideal Worst
            for j in range(ncols):
                ed_pos_ib = ed_pos_ib + (data[i][j] - ideal_best[j])**2
                ed_neg_iw = ed_neg_iw + (data[i][j] - ideal_worst[j])**2
            ed_pos_ib = ed_pos_ib**0.5
            ed_neg_iw = ed_neg_iw**0.5
            perf = ed_neg_iw/(ed_neg_iw+ed_pos_ib)
            score_list.append(perf)
        df["Topsis Score"]=score_list #Append topsis score


        #Calculate ranks
        ranks = []
        score_desc=sorted(score_list,reverse=True)\

        for i in score_list:
            ranks.append(score_desc.index(i)+1)
        df["Ranks"]=ranks
        df.to_csv(output_filename)

    except:
         sys.exit("File Not Found: You need to specify the file path. Incorrect file path detected. Recheck the full file path.")

if __name__ == "__main__":
    topsis("101903371-data.csv",[1,1,2,2,3],["+","-","+","-","+"],"101903371-result.csv")

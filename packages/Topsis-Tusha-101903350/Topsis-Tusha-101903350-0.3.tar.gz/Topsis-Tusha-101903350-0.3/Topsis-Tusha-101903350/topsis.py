import sys
import logging
import pandas as pd
import pathlib
import numpy as np
import math
from scipy.stats import rankdata

try:
    # creating logger
    logging.basicConfig(filename="101903350-logger.log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    logger = logging.getLogger('101903350')
    logger.setLevel(logging.DEBUG)

    # for storing the number of arguments
    n = len(sys.argv)
    # print(n)
    # exception when number of arguments passed > 2
    if n > 5 or n < 5:
        logger.error(
            "Wrong number of comandline arguments passed,they are greater than or less than 2,")
        sys.exit("Error in the arguments passed found, check log file")

    name = sys.argv[1]
    file = pathlib.Path(name)
    # print(file)
    if not file.is_file():
        # Input file does not exists
        logger.error(
            "Error while reading the input file, file with the mentioned name does not exists")
        sys.exit("Error while reading the input file, check log file")

    # creating dataframe of inpu file
    df = pd.read_csv(str(name))
    cols = df.columns
    w = sys.argv[2]
    impacts = sys.argv[3]
    output_filename = sys.argv[4]

    w = list(w.split(","))
    w = [float(i) for i in w]
    impacts = list(impacts.split(","))

    def calc(df, w, impacts):
        row_count = df.shape[0]
        col_count = df.shape[1]
        if col_count < 3:
            logger.error(
                " less number of columns in input file,please add more columns")
            sys.exit("Error in Input File")

        if(len(w) < col_count - 1 and len(impacts) < col_count - 1):
            logger.error(
                " less number of weights & impacts passed in the command line arguments")
            sys.exit("Error in command line arguments")
        if(len(w) > col_count - 1 and len(impacts) > col_count - 1):
            logger.error(
                " More number of weights and impacts passed in the command line arguments ")
            sys.exit("Error in command line arguments")
        if(len(w) < col_count - 1):
            logger.error(
                "Less number of weights passed in the command line arguments")
            sys.exit("Error in command line arguments")
        if(len(w) > col_count - 1):
            logger.error(
                "More number of Weights passed in the command line arguments ")
            sys.exit("Error in command line arguments")
        if(len(impacts) < col_count - 1):
            logger.error(
                "Less Number of Impacts passed in the command line arguments ")
            sys.exit("Error in command line arguments")
        if(len(impacts) > col_count - 1):
            logger.error(
                "More Number of Impacts passed in the command line arguments ")
            sys.exit("Error in command line arguments")
        for i in impacts:
            if(i == '+' or i == '-'):
                pass
            else:
                logger.error(
                    "Error in the impact argument passed during command line,please make sure the image type is '+' or '-' ")
                sys.exit("Error in command line arguments")
        normalized_df_denominator = []
        for i in range(1, col_count):
            col_denominator = 0
            for j in range(row_count):
                if isinstance(df.iloc[j][i], int) or isinstance(df.iloc[j][i], float):
                    col_denominator = col_denominator + float(df.iloc[j][i]**2)
                else:
                    logger.error(
                        "Error in the input file,the elements are either of string type or char type")
                    sys.exit("Error in input file")

            col_denominator = float(math.sqrt(col_denominator))
            normalized_df_denominator.append(col_denominator)

        for i in range(1, col_count):
            for j in range(row_count):
                if(float(normalized_df_denominator[i - 1]) == 0.0):
                    logger.error(
                        "Dividing by zero while normalising")
                    sys.exit("Can not divide by zero")
                a = df.iloc[j, i] / float(normalized_df_denominator[i - 1])
                df.iloc[j, i] = a

        for i in range(1, col_count):
            for j in range(row_count):
                a = df.iloc[j, i] * w[i - 1]
                df.iloc[j, i] = a

        # calculating ideal best and worst
        best = []
        worst = []

        for i in range(1, col_count):
            if impacts[i - 1] == '+':
                best.append(df.iloc[:, i].max())
                worst.append(df.iloc[:, i].min())
            else:
                worst.append(df.iloc[:, i].max())
                best.append(df.iloc[:, i].min())

        performance = []
        for i in range(row_count):
            sum_pos = sum((df.iloc[i, 1:] - best[:])**2)
            sum_neg = sum((df.iloc[i, 1:] - worst[:])**2)

            sum_pos = math.sqrt(sum_pos)
            sum_neg = math.sqrt(sum_neg)
            sums = sum_pos + sum_neg
            p = sum_neg / sums
            performance.append(p)

        index = rankdata(np.array(performance))
        df_new = pd.DataFrame()
        df_new = df
        df_new['Topsis Score'] = performance
        df_new['Rank'] = index
        return df_new

    df_new = calc(df, w, impacts)
    df_new.to_csv(output_filename, index=False)


except Exception as e:
    logger.error("unknown exception %s", str(e))
    sys.exit("Unknown exception has occured, check log file")

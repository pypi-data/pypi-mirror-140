import sys
import os
import pandas as pd
import logging
import math

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



class TOPSIS:

    def __init__(self, filepath, impacts, weights, output_filename) -> None:
        self.filepath    = filepath
        self.filename    = filepath.split(os.sep)[-1]
        self.impacts     = impacts
        self.weights     = weights
        self.output      = output_filename
        self.odf         = None
        self.df          = None 
        self.sp          = []
        self.sn          = []
        self.scores      = []
        self.ideal_worst = []
        self.ideal_best  = []

    def __validate_input(self):
        col_len = len(self.odf.columns)
        if col_len < 3:
            logging.error(f'{self.filename} must contain 3 or more columns.')
            return False
        if len(self.weights) != col_len - 1:
            logging.error(f'{self.filename} number of weights not equals to number of columns.')
            return False
        if len(self.impacts) != col_len - 1:
            logging.error(f'{self.filename} number of impacts not equals to number of columns.')
            return False
        for impact in self.impacts:
            if not (impact == '+' or impact == '-'):
                logging.error(f'{self.filename} Impact array can only contain + or -.')    
                return False
        return True

    def readCSV(self):
        self.odf = pd.read_csv(self.filepath)
        self.df  = self.odf.copy() # creating deep copy of df
        if self.__validate_input() == False:
            sys.exit("Stopping...")

    def storeCSV(self, output_filename):
        self.odf.to_csv(f'{output_filename}', index=False)

    def normalize(self):
        for col in self.df.columns[1:]:
            self.df[col] = self.df[col] / (math.sqrt(sum(self.df[col] ** 2)))

    def weight_assignment(self):
        for idx, col in enumerate(self.df.columns[1:]):            
            self.df[col] = self.df[col].mul(self.weights[idx])

    def find_ibw(self):
        for idx, col in enumerate(self.df.columns[1:]):            
            if self.impacts[idx] == '+':
                self.ideal_best.append(max(self.df[col]))
                self.ideal_worst.append(min(self.df[col]))
            elif self.impacts[idx] == '-':
                self.ideal_best.append(min(self.df[col]))
                self.ideal_worst.append(max(self.df[col]))

    def euclidean_distance(self):  
        for i in range(self.df.shape[0]):
            valp = 0
            valn = 0

            for idx, col in enumerate(self.df.columns[1:]):
                y  = self.df.iloc[i, idx+1]
                xp = self.ideal_best[idx]
                xn = self.ideal_worst[idx]
                
                valp += (xp - y) ** 2
                valn += (xn - y) ** 2
            
            self.sp.append(math.sqrt(valp))
            self.sn.append(math.sqrt(valn))

    def performance_score(self):
        for idx in range(len(self.sp)):
            self.scores.append(self.sn[idx] / (self.sp[idx] + self.sn[idx]))

        self.odf["Topsis Score"] = pd.DataFrame(self.scores)
    
    def find_rank(self):
        self.odf['Rank'] = (self.odf['Topsis Score'].rank(method='max', ascending=False))

    def auto(self):
        self.readCSV()
        self.normalize()
        self.weight_assignment()
        self.find_ibw()
        self.euclidean_distance()
        self.performance_score()
        self.find_rank()
        self.storeCSV(self.output)


class WrongNumberOfArgumentsNeedExactlyFour(ValueError):
    pass


def main():

    if len(sys.argv) != 5:
        raise WrongNumberOfArgumentsNeedExactlyFour

    filepath = sys.argv[1]
    weights  = list(map(int, sys.argv[2].split(",")))
    impacts  = sys.argv[3].split(",")
    output   = sys.argv[4]

    if os.path.exists(filepath):
        topsis = TOPSIS(filepath, impacts, weights, output)
        topsis.readCSV()
        topsis.normalize()
        topsis.weight_assignment()
        topsis.find_ibw()
        topsis.euclidean_distance()
        topsis.performance_score()
        topsis.find_rank()
        topsis.storeCSV(output)
    else:
        logging.error(f'{filepath} not found.')
        raise FileNotFoundError


if __name__ == '__main__':
    main()
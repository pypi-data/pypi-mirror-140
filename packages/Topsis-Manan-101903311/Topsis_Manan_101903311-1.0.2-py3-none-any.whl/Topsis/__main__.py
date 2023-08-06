import sys
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

def main():
    num = len(sys.argv)

    if num == 5:
        file = sys.argv[1]
        weights = (sys.argv[2]).split(",")
        impacts = (sys.argv[3]).split(",")
        output_file = sys.argv[4]

        try:
            hold = open(file)
            df = pd.read_csv(file)
            df1=df.loc[:,['P1','P2','P3','P4','P5']]
            final = df.copy()
            c = df.columns

            for i in impacts:
                if i not in {'+','-'}:
                    print("Impacts are not + or -")
                    break

            if len(c) < 3:
                print("File does not contain three or more columns")

            if len(c)-1 != len(weights) or len(c)-1 != len(impacts) or len(weights) != len(impacts):
                print("Number of weights , impacts and columns do not match")

            if len(weights) != 5 or len(impacts) != 5:
                print("Impacts or weights are not seperated by comma")

            for i in df1.columns:
              for j in df1.index:
                val=isinstance(df1[i][j],int)
                val1=isinstance(df1[i][j],float)
                if not val and not val1:
                  print("Values are not numeric in column ",i)
                  break

            weights = list(map(int,weights))

            sum_P1 = np.sqrt(np.square(df['P1']).sum(axis=0))
            sum_P2 = np.sqrt(np.square(df['P2']).sum(axis=0))
            sum_P3 = np.sqrt(np.square(df['P3']).sum(axis=0))
            sum_P4 = np.sqrt(np.square(df['P4']).sum(axis=0))
            sum_P5 = np.sqrt(np.square(df['P5']).sum(axis=0))

            final_P1 = (df['P1']/sum_P1)*weights[0]
            final_P2 = (df['P2']/sum_P2)*weights[1]
            final_P3 = (df['P3']/sum_P3)*weights[2]
            final_P4 = (df['P4']/sum_P4)*weights[3]
            final_P5 = (df['P5']/sum_P5)*weights[4]

            df['P1'] = final_P1
            df['P2'] = final_P2
            df['P3'] = final_P3
            df['P4'] = final_P4
            df['P5'] = final_P5

            if impacts[0] == '+':
                best_P1 = np.max(df['P1'])
                worst_P1 = np.min(df['P1'])
            else:
                best_P1 = np.min(df['P1'])
                worst_P1 = np.max(df['P1'])

            if impacts[1] == '+':
              best_P2 = np.max(df['P2'])
              worst_P2 = np.min(df['P2'])
            else:
              best_P2 = np.min(df['P2'])
              worst_P2 = np.max(df['P2'])

            if impacts[2] == '+':
              best_P3 = np.max(df['P3'])
              worst_P3 = np.min(df['P3'])
            else:
              best_P3 = np.min(df['P3'])
              worst_P3 = np.max(df['P3'])

            if impacts[3] == '+':
              best_P4 = np.max(df['P4'])
              worst_P4 = np.min(df['P4'])
            else:
              best_P4 = np.min(df['P4'])
              worst_P4 = np.max(df['P4'])

            if impacts[4] == '+':
              best_P5 = np.max(df['P5'])
              worst_P5 = np.min(df['P5'])
            else:
              best_P5 = np.min(df['P5'])
              worst_P5 = np.max(df['P5'])


            ideal_P1 = [best_P1,worst_P1]
            ideal_P2 = [best_P2,worst_P2]
            ideal_P3 = [best_P3,worst_P3]
            ideal_P4 = [best_P4,worst_P4]
            ideal_P5 = [best_P5,worst_P5]

            row = df.shape[0]

            #Calculating Euclidean Distances
            score = []
            for i in range(row):
              best_distance = ((final_P1[i]-ideal_P1[0])**2) + ((final_P2[i]-ideal_P2[0])**2) + ((final_P3[i]-ideal_P3[0])**2) + ((final_P4[i]-ideal_P4[0])**2) + ((final_P5[i]-ideal_P5[0])**2)
              worst_distance = ((final_P1[i]-ideal_P1[1])**2) + ((final_P2[i]-ideal_P2[1])**2) + ((final_P3[i]-ideal_P3[1])**2) + ((final_P4[i]-ideal_P4[1])**2) + ((final_P5[i]-ideal_P5[1])**2)

              performance = ((worst_distance)**0.5)/(((worst_distance)**0.5) + ((best_distance)**0.5))
              score.append(performance)

            hold = sorted(score,reverse=True)
            size=len(hold)
            dictt ={}
            rank=[]
            for i in range(size):
              dictt[hold[i]] = i+1


            for i in range(size):
              val = dictt[score[i]]
              rank.append(val)


            final['Topsis Score'] = score
            final['Rank'] = rank

            final.to_csv(output_file,index=False)


        except FileNotFoundError:
            print("File does not exist")

    else:
        print("Incorrect Number of parameters")


if __name__ == '__main__':
    main()

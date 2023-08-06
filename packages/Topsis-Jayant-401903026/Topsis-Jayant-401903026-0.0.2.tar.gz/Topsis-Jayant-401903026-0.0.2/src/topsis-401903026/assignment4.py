import pandas as pd
import numpy as np
import sys
if(len(sys.argv)==4):
    try:
        infile=sys.argv[1]
        df= pd.read_csv(infile)
    except:
        print("Error!!python file is Unable to open file.Please check if the files are present in the same directory or the input method is right!!")
        sys.exit(1)
    else:
        w=sys.argv[2]
        Im=sys.argv[3]
        wght=list(w.split(","))
        Impt=list(Im.split(","))
        if((len(wght)!=len(Impt) or (len(wght)!=(len(df.columns)-1)))):
            print("Wrong Input of weight or Impact")
            sys.exit(1)
        wght = list(map(int, wght))
        if((Impt.count("+") + Impt.count("-")) != len(Impt)):
            print("Wrong Input of Impact")
            sys.exit(1)
        Imp=[]
        eval_mx= df.iloc[:,1:]
        for a in Impt:
            if (a=="+"):
                Imp.append(bool(True))
            else:
                Imp.append(bool(False))
else:
    print("Incorrect Number Of Parameters")
    sys.exit(1)

class Topsis():
    evaluation_matrix = np.array([])  # Matrix
    weighted_normalized = np.array([])  # Weight matrix
    normalized_decision = np.array([])  # Normalisation matrix
    M = 0  # Number of rows
    N = 0  # Number of columns

    def __init__(self, evaluation_matrix, weight_matrix, criteria):
        # M×N matrix
        self.evaluation_matrix = np.array(evaluation_matrix, dtype="float")

        # M alternatives (options)
        self.row_size = len(self.evaluation_matrix)

        # N attributes/criteria
        self.column_size = len(self.evaluation_matrix[0])

        # N size weight matrix
        self.weight_matrix = np.array(weight_matrix, dtype="float")
        self.weight_matrix = self.weight_matrix/sum(self.weight_matrix)
        self.criteria = np.array(criteria, dtype="float")

    def stp_2(self):
        # normalized scores
        self.normalized_decision = np.copy(self.evaluation_matrix)
        sqrd_sum = np.zeros(self.column_size)
        for i in range(self.row_size):
            for j in range(self.column_size):
                sqrd_sum[j] += self.evaluation_matrix[i, j]**2
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.normalized_decision[i,
                                         j] = self.evaluation_matrix[i, j]/(sqrd_sum[j]**0.5)

    def stp_3(self):
        from pdb import set_trace
        self.weighted_normalized = np.copy(self.normalized_decision)
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.weighted_normalized[i, j] *= self.weight_matrix[j]

    def stp_4(self):
        self.worst_alternatives = np.zeros(self.column_size)
        self.best_alternatives = np.zeros(self.column_size)
        for i in range(self.column_size):
            if self.criteria[i]:
                self.worst_alternatives[i] = min(
                    self.weighted_normalized[:, i])
                self.best_alternatives[i] = max(self.weighted_normalized[:, i])
            else:
                self.worst_alternatives[i] = max(
                    self.weighted_normalized[:, i])
                self.best_alternatives[i] = min(self.weighted_normalized[:, i])

    def stp_5(self):
        self.worst_distance = np.zeros(self.row_size)
        self.best_distance = np.zeros(self.row_size)

        self.worst_distance_mat = np.copy(self.weighted_normalized)
        self.best_distance_mat = np.copy(self.weighted_normalized)

        for i in range(self.row_size):
            for j in range(self.column_size):
                self.worst_distance_mat[i][j] = (self.weighted_normalized[i][j]-self.worst_alternatives[j])**2
                self.best_distance_mat[i][j] = (self.weighted_normalized[i][j]-self.best_alternatives[j])**2
                
                self.worst_distance[i] += self.worst_distance_mat[i][j]
                self.best_distance[i] += self.best_distance_mat[i][j]

        for i in range(self.row_size):
            self.worst_distance[i] = self.worst_distance[i]**0.5
            self.best_distance[i] = self.best_distance[i]**0.5

    def stp_6(self):
        np.seterr(all='ignore')
        self.worst_similarity = np.zeros(self.row_size)

        for i in range(self.row_size):
            # calculate the similarity to the worst condition
            self.worst_similarity[i] = self.worst_distance[i] / \
                (self.worst_distance[i]+self.best_distance[i])

    
    def ranking(self, data):
        return [i+1 for i in data.argsort()]

    def rank_to_worst_similarity(self):
        # return rankdata(self.worst_similarity, method="min").astype(int)
        return self.ranking(self.worst_similarity)

    def calc(self):
        self.stp_2()
        self.stp_3()
        self.stp_4()
        self.stp_5()
        self.stp_6()

t = Topsis(eval_mx, wght, Imp)

t.calc()
df["Topsis Score"]= t.worst_similarity
df["Rank"]=t.rank_to_worst_similarity()
df.to_csv("401903026-output.csv")


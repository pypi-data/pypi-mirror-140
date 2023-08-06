import sys
import numpy as np
import pandas as pd
import warnings
if len(sys.argv) != 5:
    raise Exception('Give correct number of parameters')
    sys.exit()
    
try:
    with open(sys.argv[1]) as f:
        print("File does exists")
        
except FileNotFoundError:
    raise Exception('Give correct file')
    sys.exit()
     
except:
    raise Exception('Give correct file')
    sys.exit()

dataframe = pd.read_csv(sys.argv[1])

if len(dataframe.columns) <= 3:
	raise Exception('Incorrect no. of columns ')
    

numberOfCols = len(dataframe.columns)-1
w = sys.argv[2].split(',')
i = sys.argv[3].split(',')
for j in range(len(i)):
    if i[j]=="+":
        i[j]="1"
    elif i[j]=="-":
        i[j]="-1"
    else:
        raise Exception('impacts provided are Invalid')
         
w_len = len(w) 
i_len = len(i)
result_file = sys.argv[4]

dataframe.iloc[:,1:].apply(lambda h:pd.to_numeric(h,errors='raise').notnull().all())
if(w_len!=i_len or i_len!=numberOfCols or numberOfCols!=w_len):
    raise Exception('weight and impact and columns numbers are not equal')
print(numberOfCols)
print(w)
print(i)
print(dataframe)


w = [int(i) for i in w]

i = [int(j) for j in i]

class Topsis():
    evaluation_matrix = np.array([])  
    weighted_normalized = np.array([])  
    normalized_decision = np.array([])  
    M = 0  
    N = 0  
    def __init__(self, evaluation_matrix, weight_matrix, criteria):
        
        self.evaluation_matrix = np.array(evaluation_matrix, dtype="float")
        self.row_size = len(self.evaluation_matrix)
        self.column_size = len(self.evaluation_matrix[0])
        self.weight_matrix = np.array(weight_matrix, dtype="float")
        self.weight_matrix = self.weight_matrix/sum(self.weight_matrix)
        self.criteria = np.array(criteria, dtype="float")

   

    def step_2(self):
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

   

    def step_3(self):
        from pdb import set_trace
        self.weighted_normalized = np.copy(self.normalized_decision)
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.weighted_normalized[i, j] *= self.weight_matrix[j]

    

    def step_4(self):
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

    

    def step_5(self):
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

    

    def step_6(self):
        np.seterr(all='ignore')
        self.worst_similarity = np.zeros(self.row_size)
        self.best_similarity = np.zeros(self.row_size)

        for i in range(self.row_size):
            
            self.worst_similarity[i] = self.worst_distance[i] / \
                (self.worst_distance[i]+self.best_distance[i])

            
            self.best_similarity[i] = self.best_distance[i] / \
                (self.worst_distance[i]+self.best_distance[i])
    
    def ranking(self, data):
        return [i+1 for i in data.argsort()]

    def rank_to_worst_similarity(self):
        
        return self.ranking(self.worst_similarity)

    def rank_to_best_similarity(self):
        
        return self.ranking(self.best_similarity)

    def calc(self):
        print("Step 1\n", self.evaluation_matrix, end="\n\n")
        self.step_2()
        print("Step 2\n", self.normalized_decision, end="\n\n")
        self.step_3()
        print("Step 3\n", self.weighted_normalized, end="\n\n")
        self.step_4()
        print("Step 4\n", self.worst_alternatives,
              self.best_alternatives, end="\n\n")
        self.step_5()
        print("Step 5\n", self.worst_distance, self.best_distance, end="\n\n")
        self.step_6()
        print("Step 6\n", self.worst_similarity,
              self.best_similarity, end="\n\n")



b= Topsis(dataframe.iloc[:,1:],w,i)
b.calc()
dataframe['Topsis Score'] = b.worst_similarity
dataframe['Rank'] = b.rank_to_worst_similarity()
print(dataframe)
dataframe.to_csv(result_file,index=False)
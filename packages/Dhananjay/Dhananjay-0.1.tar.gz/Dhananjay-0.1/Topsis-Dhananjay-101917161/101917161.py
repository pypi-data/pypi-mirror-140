import sys
import numpy as np
import pandas as pd
import warnings


if len(sys.argv) != 5:
    raise Exception('Provide correct number of parameters')
    sys.exit()
    #logs.error("More number of parameters are passed then expected!!!")
	#raise Exception('Provide correct number of parameters as input!!!')
    
try:
    with open(sys.argv[1]) as f:
        print("File exists!!")
        #logs.error("File exists")
except FileNotFoundError:
    raise Exception('Provide correct file')
    sys.exit()
     #print('File does not exist!!!')
    #logs.error("File does not exist!!!")
except:
    raise Exception('Provide correct file')
    sys.exit()
	#print('Something went wrong!!!')
    #logs.error('Something went wrong!!!')	



df = pd.read_csv(sys.argv[1])

if len(df.columns) <= 3:
	raise Exception('Inappropriate no. of columns ')
    #sys.exit()
    #logs.error('Invalid no. of columns')

no_of_col = len(df.columns)-1
w = sys.argv[2].split(',')
i = sys.argv[3].split(',')
for j in range(len(i)):
    if i[j]=="+":
        i[j]="1"
    elif i[j]=="-":
        i[j]="-1"
    else:
        raise Exception('Invalid impacts provided')
         
w_len = len(w) 
i_len = len(i)
result_file = sys.argv[4]

df.iloc[:,1:].apply(lambda h:pd.to_numeric(h,errors='raise').notnull().all())
if(w_len!=i_len or i_len!=no_of_col or no_of_col!=w_len):
    raise Exception('weight and impact and columns numbers are not equal')
print(no_of_col)
print(w)
print(i)
print(df)


w = [int(i) for i in w]

i = [int(j) for j in i]

class Topsis():
    evaluation_matrix = np.array([])  # Matrix
    weighted_normalized = np.array([])  # Weight matrix
    normalized_decision = np.array([])  # Normalisation matrix
    M = 0  # Number of rows
    N = 0  # Number of columns

    '''
	Create an evaluation matrix consisting of m alternatives and n criteria,
	with the intersection of each alternative and criteria given as {\displaystyle x_{ij}}x_{ij},
	we therefore have a matrix {\displaystyle (x_{ij})_{m\times n}}(x_{{ij}})_{{m\times n}}.
	'''

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

    '''
	# Step 2
	The matrix {\displaystyle (x_{ij})_{m\times n}}(x_{{ij}})_{{m\times n}} is then normalised to form the matrix
	'''

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

    '''
	# Step 3
	Calculate the weighted normalised decision matrix
	'''

    def step_3(self):
        from pdb import set_trace
        self.weighted_normalized = np.copy(self.normalized_decision)
        for i in range(self.row_size):
            for j in range(self.column_size):
                self.weighted_normalized[i, j] *= self.weight_matrix[j]

    '''
	# Step 4
	Determine the worst alternative {\displaystyle (A_{w})}(A_{w}) and the best alternative {\displaystyle (A_{b})}(A_{b}):
	'''

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

    '''
	# Step 5
	Calculate the L2-distance between the target alternative {\displaystyle i}i and the worst condition {\displaystyle A_{w}}A_{w}
	{\displaystyle d_{iw}={\sqrt {\sum _{j=1}^{n}(t_{ij}-t_{wj})^{2}}},\quad i=1,2,\ldots ,m,}
	and the distance between the alternative {\displaystyle i}i and the best condition {\displaystyle A_{b}}A_b
	{\displaystyle d_{ib}={\sqrt {\sum _{j=1}^{n}(t_{ij}-t_{bj})^{2}}},\quad i=1,2,\ldots ,m}
	where {\displaystyle d_{iw}}d_{{iw}} and {\displaystyle d_{ib}}d_{{ib}} are L2-norm distances 
	from the target alternative {\displaystyle i}i to the worst and best conditions, respectively.
	'''

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

    '''
	# Step 6
	Calculate the similarity
	'''

    def step_6(self):
        np.seterr(all='ignore')
        self.worst_similarity = np.zeros(self.row_size)
        self.best_similarity = np.zeros(self.row_size)

        for i in range(self.row_size):
            # calculate the similarity to the worst condition
            self.worst_similarity[i] = self.worst_distance[i] / \
                (self.worst_distance[i]+self.best_distance[i])

            # calculate the similarity to the best condition
            self.best_similarity[i] = self.best_distance[i] / \
                (self.worst_distance[i]+self.best_distance[i])
    
    def ranking(self, data):
        return [i+1 for i in data.argsort()]

    def rank_to_worst_similarity(self):
        # return rankdata(self.worst_similarity, method="min").astype(int)
        return self.ranking(self.worst_similarity)

    def rank_to_best_similarity(self):
        # return rankdata(self.best_similarity, method='min').astype(int)
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



b= Topsis(df.iloc[:,1:],w,i)
b.calc()
df['Topsis Score'] = b.worst_similarity
df['Rank'] = b.rank_to_worst_similarity()
print(df)
df.to_csv(result_file,index=False)


#Lorem ipsum dolor sit amet consectetur adipisicing elit. Possimus ratione atque ab quod voluptas repellendus nam nulla, quam id iure libero minus commodi porro quis? Dolor animi quasi totam hic aut deleniti. Ipsa possimus quos quas rem, autem officiis accusamus repudiandae exercitationem laborum dolor ratione quis dolores ullam labore repellat itaque accusantium earum! Voluptate quae fugiat quibusdam voluptatibus maiores amet, cupiditate corrupti ipsam repellendus qui aliquam quisquam dicta odio dolor quod. Rem tempora perferendis laboriosam ducimus, sit sed ab natus amet pariatur suscipit labore. Vero esse, cumque tempore quos obcaecati incidunt sapiente quidem, ex fugiat voluptas dolores laboriosam eaque eum ipsum totam error magnam ipsa explicabo perferendis repellat. Magni laudantium maiores nesciunt soluta ullam? Asperiores repellat autem natus doloribus sed officia impedit molestias nulla repellendus! Et ad illo deleniti sed a ratione officia sequi reiciendis velit at, earum aut porro non facere aliquam perferendis dicta illum vero nihil repudiandae veritatis ipsa commodi reprehenderit! Suscipit tempora iste amet impedit. Voluptates, unde aspernatur, saepe alias inventore repellendus quam, nam perferendis debitis accusantium sit? Rem, dignissimos modi, laudantium distinctio aspernatur dolore aliquam nihil sunt praesentium veniam deserunt sed minus quam labore alias nam delectus. Autem nostrum aliquam voluptatibus perferendis neque, inventore blanditiis qui quaerat vitae nesciunt tempore ullam ipsum corrupti nam odio temporibus omnis cum magni. Cum doloremque beatae quos harum praesentium quibusdam fugit tempora eaque veniam dignissimos atque, obcaecati ab nemo quae soluta ad. Maiores porro omnis accusamus ipsam officiis cum ipsa consequatur reprehenderit. Nisi ad nemo vel explicabo. Aspernatur laboriosam voluptas quaerat dicta suscipit doloremque illo culpa magnam quod iure veniam temporibus nulla, pariatur quo similique sed placeat. Ipsam incidunt maiores hic odio reprehenderit! Laboriosam cumque quam enim iusto aliquid maiores in incidunt necessitatibus fuga consectetur tenetur expedita, totam fugiat nihil iure autem odit nesciunt quae? Quisquam commodi doloremque dolore natus ipsa minus vel quos, iusto corporis alias consequatur unde odio, maxime et dolor repellendus error aliquid? Dolores quibusdam voluptatum dolore nemo necessitatibus quisquam saepe, sed voluptatibus nisi earum harum qui iusto, placeat, velit ipsum accusantium perspiciatis unde possimus itaque! Ex placeat deserunt iure iusto illum repellendus sapiente id rem optio corrupti assumenda dolorem aliquid officiis aperiam quibusdam, aliquam quod error? Necessitatibus porro quas maiores sapiente, veniam ut atque numquam quidem, alias praesentium fugiat sunt, omnis voluptates vel assumenda nostrum. Architecto deserunt, fugit odit nobis perspiciatis cum praesentium, hic ad vero deleniti dolores quidem, blanditiis perferendis qui temporibus unde. Voluptatum animi corporis ipsam similique officiis et sit sint, qui cumque quisquam! Aperiam beatae atque error consectetur laudantium. Libero autem dolore id maiores harum vero labore amet ullam? Atque repellendus expedita nostrum velit, magnam mollitia illum, autem dolorum ut aut sed vitae alias possimus error fugit doloribus vero ad. Provident suscipit, in voluptatibus autem cumque nemo ex sint sapiente necessitatibus porro odio! Asperiores officiis sunt reiciendis atque optio debitis, enim maxime praesentium totam possimus illum cumque consequuntur saepe nam quo temporibus id libero quae accusantium reprehenderit veniam. Fugiat veritatis expedita porro pariatur tempora nemo veniam eos provident, debitis quidem voluptatum, fugit a.
#Lorem ipsum dolor sit, amet consectetur adipisicing elit. Molestiae sint ex maxime, rerum possimus eveniet quibusdam soluta saepe dolorum molestias minus officiis laudantium consectetur labore quia ab expedita sed. Magni provident voluptates odit cupiditate sint ipsam quae necessitatibus, in cumque, id pariatur possimus quos, tenetur molestiae repudiandae consequatur. Praesentium ipsam hic tenetur fugit sint excepturi libero esse reprehenderit tempora, quis assumenda. Ab, non natus? Non cum assumenda, obcaecati voluptates ex nulla in totam, nostrum, voluptatem ullam exercitationem rerum. Aliquam, possimus. Deserunt laudantium incidunt voluptates labore pariatur praesentium, laborum corporis quia, cumque, sequi eligendi adipisci amet ipsum expedita! Ex debitis earum dolorum asperiores fugiat autem cumque reprehenderit vitae, aliquid, sed vero omnis expedita inventore at! Deserunt, et commodi ratione error odio quibusdam ad beatae quas soluta nulla ut, sapiente fugiat nemo natus? Perferendis nihil ipsam ullam similique. Officiis, minima delectus. Corrupti eveniet odit qui nobis praesentium, explicabo quae nam eos aliquam minus tempora deserunt quo vero id voluptatibus doloribus accusantium sed repellendus molestias ab quidem nulla ex cupiditate voluptatem. Nesciunt eveniet voluptates voluptatibus quaerat unde maiores, perferendis libero. Officia magnam tenetur sint facere quaerat, odit illum veritatis architecto culpa quasi unde pariatur, natus dolorum, fugit assumenda. Quam, possimus unde nulla maiores laboriosam doloremque eligendi sit reprehenderit ipsa magni earum incidunt id aliquam fugiat deleniti reiciendis voluptatibus quod? Totam suscipit earum, in quos, iste sit voluptate debitis esse saepe repellendus magni soluta deserunt harum sunt corrupti, labore dolores facere adipisci obcaecati ad voluptates velit laborum. Illo minima eum, ex quos dolor dolorem iusto, assumenda nemo, ipsa ducimus quae voluptatem velit cupiditate sit placeat veritatis. Fugit reiciendis porro ad neque ut laboriosam inventore quod vitae debitis! Enim laborum doloremque aperiam. Nostrum reprehenderit voluptates eligendi qui deserunt beatae eum perferendis iure inventore error consequatur assumenda veniam autem nesciunt esse ratione sit aperiam saepe eaque, id consequuntur ad non molestias sapiente. Debitis possimus esse vitae magni, quo nemo magnam dolorum fugit porro tempore harum similique ad dolore, non id quas autem vel. Impedit voluptate libero pariatur modi dolorum eaque enim dolores explicabo labore ipsam, soluta nihil! Modi magni architecto, cum vero numquam incidunt! Laboriosam nobis vero modi repellendus in quasi maxime, distinctio laborum? Recusandae suscipit aut minima vero odit veniam cumque corporis aspernatur, temporibus maxime impedit, labore quas, similique ab sequi cum voluptate facilis corrupti neque laudantium et ullam adipisci. Quos quisquam aperiam eos aliquam, minus ratione sed nam enim atque expedita fugiat qui consequuntur commodi fuga unde quis maxime iusto molestiae error dolor, tempora nisi. Possimus excepturi accusamus, quasi neque odit at cupiditate doloremque dolorum fuga voluptatem illum magni nobis inventore accusantium iure sunt! Deleniti cupiditate, asperiores voluptate aspernatur distinctio placeat, fugit ipsum deserunt beatae minima quaerat. Ea veniam officia voluptas amet perferendis dolore omnis exercitationem aliquam quia. Corrupti quaerat, voluptatem blanditiis praesentium, reiciendis dolore harum delectus tenetur eius architecto ducimus obcaecati aspernatur nostrum adipisci animi maiores. Commodi maxime mollitia distinctio praesentium iste aliquam tempora possimus optio exercitationem neque quos, nam dolore pariatur odit fugit ad molestias ipsum dolores vitae perferendis eius. Alias, a!
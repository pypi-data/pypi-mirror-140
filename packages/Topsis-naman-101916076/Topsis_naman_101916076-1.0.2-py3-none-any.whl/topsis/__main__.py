
import sys
import pandas as pd

from math import sqrt

def main(sysarglist):
	
	if len(sys.argv)!=5:
	   
	    raise Exception("Sorry, No. of input parameters must be 5\n")

	try:
	    with open(sys.argv[1], 'r') as file1:
	        file=pd.read_csv(file1)
	except FileNotFoundError:
	    print(" File not found  \n")


	weights=list(map(int,sys.argv[2].split(',')))


	impacts=list(sys.argv[3].split(','))


	punct_dict = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '+': True, '*': True,'-': True, '=': True}
	punct_dict2 = {'.':True,'@': True, '^': True, '!': True, ' ': True, '#': True, '%': True,'$': True, '&': True, ')': True, '(': True, '*': True, '=': True}

	def char_check(new_list, punct_dict):
	    for item in new_list:
	        for char in item:
	            if char in punct_dict:
	                return False

	def string_check(comma_check_list, punct_dict):
	    for string in comma_check_list:
	        new_list = string.split(",")
	        if char_check(new_list, punct_dict) == False:
	            print("Values not comma separated")
	            exit()

	string_check(sys.argv[2], punct_dict)
	string_check(sys.argv[3], punct_dict2)

	df,temp_dataset = pd.DataFrame(data=file),pd.DataFrame(data=file)
	#numeric handling
	def is_float(x):
	    try:
	        float(x)
	    except :
	        return False
	    return True

	for co in df.columns:
	    if(co!=df.columns[0]):
	        df=df[df[co].apply(lambda x: is_float(x))]
	print("Handled non-numeric data\n")
	res = df.copy(deep=True)

	nCol=len(df.columns)

	if nCol < 3:
	        print("ERROR : Input file have less then 3 columns")
	        exit(1)


	for i in impacts:
	    if not (i == '+' or i == '-'):
	        print("ERROR : In impact array please check again")
	        exit(1)


	if nCol != len(weights)+1 or nCol != len(impacts)+1:
	    print(
	        "ERROR : Number of weights, number of impacts and number of columns not same")
	    exit(1)

	for im in df.columns:
	    if(im!=df.columns[0]):
	        df[im] = pd.to_numeric(df[im])



	def Normalize(df, nCol, weights):
	    for i in range(1, nCol):
	        temp = 0
	        
	        for j in range(len(df)):
	            temp = temp + df.iloc[j, i]**2
	        temp = sqrt(temp)
	        # Weighted Normalizing a element
	        for j in range(len(df)):
	            df.iat[j, i] = (float(df.iloc[j, i])) / float(temp)*float(weights[i-2])
	    

	Normalize(df,nCol,weights)

	def Calc_Values(df, nCol, weights):
	    p_sln = (df.max().values)[1:]
	    n_sln = (df.min().values)[1:]
	    for i in range(1, nCol):
	        if impacts[i-2] == '-':
	            p_sln[i-1], n_sln[i-1] = n_sln[i-1], p_sln[i-1]
	    return p_sln, n_sln

	p_sln, n_sln = Calc_Values(df, nCol, impacts)

	# calculating topsis score
	score = [] # Topsis score
	pp = [] # distance positive
	nn = [] # distance negative

	 
	# Calculating distances and Topsis score for each row
	for i in range(len(df)):
	 temp_p, temp_n = 0, 0
	 for j in range(1, nCol):
	     temp_p = temp_p + (p_sln[j-1] - df.iloc[i, j])**2
	     temp_n = temp_n + (n_sln[j-1] - df.iloc[i, j])**2
	 temp_p, temp_n = temp_p*0.5, temp_n*0.5
	 score.append(temp_n/(temp_p + temp_n))
	 nn.append(temp_n)
	 pp.append(temp_p)

	# Appending new columns in dataset   

	 
	res['Topsis Score'] = score



	# calculating the rank according to topsis score
	res['Rank'] = (res['Topsis Score'].rank(method='max', ascending=False))
	res = res.astype({"Rank": int})


	res.to_csv(sys.argv[4],index=False)


if __name__ == "__main__":
    sysarglist = sys.argv
     
    main(sysarglist)
    
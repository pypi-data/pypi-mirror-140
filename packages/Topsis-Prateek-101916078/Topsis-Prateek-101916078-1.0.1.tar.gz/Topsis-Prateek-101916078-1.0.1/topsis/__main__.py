import sys
import pandas as pd
from math import sqrt




def main(arglist):
    # Prateek Rai
    # 101916078
    # 3CS11
    # Assignment-4 Topsis
    # First question

    # parameters to handle during input
    parameters_passed = len(arglist)






    # exception handling


    # Correct number of parameters (inputFileName, Weights, Impacts, resultFileName) : 
    # Show the appropriate message for wrong inputs : 
    if(parameters_passed!=5):
        # log file entry wrong parameter
        print('Wrong number of parameters parsed, Use python 101916078.py 101916078-data.csv "1,1,1,2" "+,+,-,+" 101916078-result.csv only\n')
        sys.exit()
    else :
        # correct number of parameters 
        print("\nNumber of Parameters Correct..\n")
        





    # Handling of “File not Found” exception : 
    input_file=arglist[1]
    try:
        data=pd.read_csv(input_file)
        
        # print(data)
    except:
        # log file entry for file not found
        print("File not found..\n")
        print("Error occured : ",sys.exc_info()[0],"\n")
        sys.exit()

    print("File read..\n")





    # Input file must contain three or more columns : 
    number_of_columns=len(data.columns)
    if(number_of_columns<3):
        # log file entry for having less than three columns
        print("The input file should have three or more than three columns. Please re-run with right input file.\n")
        sys.exit()
    else :
        print("Correct Number of columns..\n")





    # From 2nd to last columns must contain numeric values only (Handling of non-numeric values) :
    # deleting row that has a non numeric value
    def is_float(x):
        try:
            float(x)
        except :
            return False
        return True

    for co in data.columns:
        if(co!=data.columns[0]):
            data=data[data[co].apply(lambda x: is_float(x))]
    
    print("Handled non-numeric data\n")




    # Impacts and weights must be separated by ‘,’ (comma).
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
                print("Weights/Impacts should be comma separated as string inputs. e.g.: '1,2,3,1'\n")
                sys.exit()

    string_check(arglist[2], punct_dict)
    string_check(arglist[3], punct_dict2)



    # Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same :
    # getting weights


    weights=list(arglist[2].split(','))
    number_of_weights=len(weights)
    # print(weights)

    # getting impacts


    impacts=list(arglist[3].split(','))

    number_of_impacts=len(impacts)
    # print(impacts)

    # getting number of columns from 2nd to last
    number_of_imp_columns=len(data.columns)-1
    # print(number_of_imp_columns)

    if(number_of_weights==number_of_impacts==number_of_imp_columns):
        print("Number of impacts and weights are correct.\n")
    else:
        print("Number of impacts, weights and columns are not same.\n")
        sys.exit()




    # Impacts must be either +ve or -ve.
    test=['+','-']
    for im in impacts:
        if(im in test):
            continue
        else:
            print("Impacts should be in + and - only.\n")
            sys.exit()









    # main code
    for im in data.columns:
        if(im!=data.columns[0]):
            data[im] = pd.to_numeric(data[im])



    res = data.copy(deep=True)
    df = pd.DataFrame(data)

    nCol=len(df.columns)


    def Normalize(df, nCol, weights):
        for i in range(1, nCol):
            temp = 0
            
            for j in range(len(df)):
                temp = temp + df.iloc[j, i]**2
            temp = sqrt(temp)
            # Weighted Normalizing a element
            for j in range(len(df)):
                df.iat[j, i] = (float(df.iloc[j, i])) / float(temp)*float(weights[i-2])
        print(df)

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

    
    df['Topsis Score'] = score

    # calculating the rank according to topsis score
    df['Rank'] = (df['Topsis Score'].rank(method='max', ascending=False))
    df = df.astype({"Rank": int})


    res['Topsis Score']=df['Topsis Score']
    res['Rank']=df['Rank']
    print(df)
    res.to_csv(arglist[4],index=False)




    # success
    print("Done...\n")





    # close files
    sys.exit()



if __name__ == '__main__':
    sysarglist = sys.argv
    main(sysarglist)
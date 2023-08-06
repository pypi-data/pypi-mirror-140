def topsis(file_name, weight, impact, output):
    try:

        #importing all the necessary libraries
        import pandas as pd
        import sys
        import warnings
        import numpy as np

    except:
        print("Welcome to the code!!!")
        
    else:
        
        #wrong type of input file
        try:
            if "csv" not in file_name:
                raise Exception
                
        except:
            print("The input file you gave is not csv file!!!")
            
        else:
            
            try:
                #read original file
                data = pd.read_csv(file_name)
                
            except:
                print("File does not exist!!!")
                
            else:
                #input file containing not 3 or more number of inputs  
                try:
                    if len(data.columns) < 3:
                        raise Exception
                
                except:
                    print('Number of columns in the input file is not 3 or more than 3!!!')
                    
                else:
                
                    try:
                        for cols in data.columns[1:]:
                            pd.to_numeric(data[cols]) #raises error as well

                    except:
                        print('From 2nd to last columns must contain numeric values only!!!')
                    else:
                        
                        try:
                            we = list(weight.split(','))
                            I = list(impact.split(','))
                                    
                            w = []
                            for i in we:
                                w.append(float(i))
                            
                        except:
                            print('weights must be separated by ‘,’ !!!')
                            
                        else:
                            try:
                                for ele in I:
                                    if(ele != '+' and ele != '-' and ele != ','):
                                        raise Exception
                            except:
                                print('Impacts must be either +ve or -ve and separated by comma!!!')
                            else:
                                try:
                                    if( len(data.columns)-1 != len(we) or len(data.columns)-1 != len(I) ):
                                        raise Exception
                                except:
                                    print('Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same')
                                
                                else:
                                    #normalization
                                    for col in data.columns[1:]:
                                        data[col] = data[col]/np.sqrt(np.sum(np.square(data[col])))
                                        
                                    #via enumerate we can get the value and the index as well
                                    #and via that index we can get the specified value from the weight list
                                    #enumerate does the ++ and initialaztion from 0 by default
                            
                                    w = []
                                    for i in we:
                                        w.append(float(i))

                                    for i,col in enumerate(data.columns[1:]):
                                        data[col]=data[col]*w[i]
                                        
                                    ideal_best = []
                                    ideal_worst = []

                                    #finding the best and the worst values
                                    for i,col in enumerate(data.columns[1:]):
                                        if I[i] == '-':
                                            ideal_best.append(data[col].min())
                                            ideal_worst.append(data[col].max())
                                        else:
                                            ideal_best.append(data[col].max())
                                            ideal_worst.append(data[col].min())
                                            
                                    #defining the euclidean function
                                    def Euclidean(row1,row2):
                                        return np.sqrt(np.sum(np.square(row1-row2)))
                                        
                                    df1 = data.iloc[:,1:6]
                                    print(df1)
                                    
                                    Splus = np.array([Euclidean(ideal_best,row) for row in df1.values ])
                                    Sminus = np.array([Euclidean(ideal_worst,row) for row in df1.values ])
                                    
                                    PScore = Sminus/(Sminus+Splus)
                                    data['Topsis Score'] = PScore        
                        
                                    data['Rank'] = data['Topsis Score'].rank(ascending=False)
                                    
                                    #putting all the data to the output file
                                    data.to_csv(output, index = False)
                                    return data

                        
                        

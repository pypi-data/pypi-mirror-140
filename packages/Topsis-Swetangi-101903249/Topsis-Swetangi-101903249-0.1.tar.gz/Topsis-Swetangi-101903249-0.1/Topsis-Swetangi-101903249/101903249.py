import pandas as pd
import numpy as np

class topsis():
    
    def __init__(self,input,weights,impacts):
        
        self.input_file=input
        self.w=weights
        self.imp=impacts
    
    def result(self):
        try:
            df=pd.read_csv(self.input_file)
        except:
            err=['Error: File '+str(self.input_file)+' Not Found']
            print(err)
            exit()

        if any(True for char in self.w if char in '@^! #%$&)(+*-="'):
            err=['Error: Weights are not separated by a comma']
            print(err)
            exit()
        else:
            weight = self.w.split(",")


        if any(True for char in self.imp if char in '@^! #%$&)(*="'):
            err=['Error: Impacts are not given correctly']
            print(err)
            exit()
        else:
            impacts = self.imp.split(",")
        
        
        for imp in impacts:
            if(imp=='+' or imp=='-'):
                continue
            else:
                print("Impacts must be either positive or negative!")
                exit()

        data= df.drop(df.columns[[0]], axis = 1)
        
        if len(weight)!=len(impacts) or len(impacts)!=data.shape[1] or len(weight)!=data.shape[1]:
            err=['Error: Wrong number of inputs in weight/impacts']
            print(err)
            exit()

        if(df.shape[1]<3):
            err=['Error: The number of columns in the given input file are not equal to or more than 3']
            print(err)
            exit()


        if data.applymap(np.isreal).all(1).sum() != data.shape[0]:
            err=['Error: Non-numeric column values occur']
            print(err)
            exit()

        for col in data.columns:
            data[col] = data[col]/np.sqrt(np.sum(np.square(data[col])))


        for i,col in enumerate(data.columns):
            data[col]=data[col]*int(weight[i])
            

        best=[]
        worst=[]
        j=0
        
        for i in impacts:
            if(i =="+"):
                best.append(data.iloc[:,[j]].max()[0])
                worst.append(data.iloc[:,[j]].min()[0])
                j=j+1
            elif (i=="-"):
                best.append(data.iloc[:,[j]].min()[0])
                worst.append(data.iloc[:,[j]].max()[0])
                j=j+1
            else:
                error =["Error: The 'impacts' input is wrong."]
                print(error)
                exit()

        ideal_best = np.array(best)
        ideal_worst = np.array(worst)

        def Euclidean(ideal,row):
            return np.sqrt(np.sum(np.square(ideal-row)))

        Splus = np.array([Euclidean(ideal_best,row) for row in data.values ])
        Sminus = np.array([Euclidean(ideal_worst,row) for row in data.values ])

        PScore = Sminus/(Sminus+Splus)
        data['Topsis Score'] = PScore
        df['Topsis Score']= PScore

        data["Rank"] = data["Topsis Score"].rank(ascending=False)
        df["Rank"] = data["Rank"]

        return df
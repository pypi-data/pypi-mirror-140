import pandas as pd
import math



class find_topsis:
    # init method or constructor 
    def __init__(self, *argv):
        argv=list(argv)
        # print(type(argv[0]))
        
        f = open("log.txt", "w")
        f.write("module started running : "+'\n')

        if len(argv) > 4:
            f.write("less no. of arguments needed" + '\n')
            exit()
        elif len(argv) < 4:
            f.write('all inputs not given' + '\n')
            exit()
        else:
            pass

        inputfile = argv[0]


        try:
            # reading excel file
            data = pd.DataFrame(pd.read_excel(inputfile))
        except FileNotFoundError:
            f.write("Given File not found." + '\n')
            exit()

        # savind data as csv
        data.to_csv("input-data.csv")

        # storing shape of dataframe
        s=data.shape
        if s[1]<3:
            f.write("Input file must contain three or more columns" + '\n')
            exit()


        # handling null values
        # data.fillna(0)
        # data.fillna(method='ffill')
        # data.fillna(method='bfill')
        data.interpolate()

        #assigning weights
        # # weights=[1]*(s[1]-1)
        weights=list(argv[1])

        #assigning impacts
        # impacts=['+']*(s[1]-1)
        impacts=list(argv[2])

        # Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same.

        if len(weights)!=len(impacts) or len(impacts)!=(s[1]-1):
            f.write("Number of weights, number of impacts and number of columns (from 2nd to last columns) must be same." + '\n')
            exit()

        # impacts must be either +ve or -ve.
        for x in impacts:
            if x!="+" and x!="-":
                f.write("impacts must be either +ve or -ve." + '\n')
                exit()

        # Impacts and weights must be separated by ‘,’ (comma).
        # wt=list(sys.argv[2])[1::2]
        # it=list(sys.argv[3])[1::2]
        # if it!=[","]*(len(impacts)-1) or wt!=[","]*(len(weights)-1):
        #     f.write("Impacts and weights must be separated by ‘,’ (comma)." + '\n')
        #     exit()


        #noramlized decision matrix including rss
        for y in range(1,s[1]):
            tmp=0
            for x in range(s[0]):
                tmp+=data.iloc[x,y]**2
            tmp=math.sqrt(tmp)
            for z in range(s[0]):
                data.iloc[z,y]=data.iloc[z,y]/tmp

        #weight assignment
        for y in range(1,s[1]):
            data.iloc[:,y]=data.iloc[:,y]*int(weights[y-1])

        #find ideal beat and ideal worst
        ibest=[0]*(s[1]-1)
        iworst=[0]*(s[1]-1)

        for y in range(1,s[1]):
            if impacts[y-1]=="+":
                ibest[y-1]=max(data.iloc[:,y])
                iworst[y-1]=min(data.iloc[:,y])
            elif impacts[y-1]=="-":
                ibest[y-1]=min(data.iloc[:,y])
                iworst[y-1]=max(data.iloc[:,y])

        #euclidean distance and pandn
        spos=[0]*s[0]
        sneg=[0]*s[0]
        pandn=[0]*s[0]

        for x in range(s[0]):
            ptmp=0
            ntmp=0
            for y in range(1,s[1]):
                ptmp+=(data.iloc[x,y]-ibest[y-1])**2
                ntmp+=(data.iloc[x,y]-iworst[y-1])**2
            spos[x]=ptmp
            sneg[x]=ntmp
            pandn[x]=ptmp+ntmp

        #performance score
        ps=[0]*s[0]

        for x in range(len(pandn)):
            ps[x]=sneg[x]/(spos[x]+sneg[x])

        #topsis score
        pscopy=sorted(ps,reverse=True)

        #ranking
        rank=[0]*s[0]

        for x in range(len(ps)):
            rank[x]=pscopy.index(ps[x])+1

        # addig score and rank to data
        data["Topsis Score"]=ps
        data["Rank"]=rank

        #rounding to 3decimal pts.
        data=round(data,3)

        #saving result as csv
        outputfile=argv[3]
        # data.to_csv("101903245-result.csv")
        data.to_csv(outputfile)

        f.write("file executed successfully." + '\n')
        exit()

 # python topsis.py data.xlsx "1,1,1,2,1" "+,+,-,+,+" 101903245-output.csv
if __name__ == "__main__":
    find_topsis("data.xslx",[1,1,2,3],["+","+","-","-"],"output.csv")
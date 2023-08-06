import pandas as pd
import math
import sys
def Topsis_abhay():
    error=0
    print("program started")
    n = len(sys.argv)

    if(n!=5):
        print("no of input parameters are not 4 ")
        error=error+1

    arg=sys.argv
    df = pd.read_csv(sys.argv[1])
    if (arg[1]!="101903685.py"):
        print("python file does not match with your rollno")
        error=error+1

    if (arg[1]!="101903685-data.csv"):
        print("Data csv file does not match with your rollno")
        error=error+1

    if (arg[4] != "101903685-result.csv"):
        print("Result  csv file does not match with your rollno" )
        error = error + 1


    col = df.columns
    if len(col) < 3:
      print("input has less than the 3 columns")
    df1 = df.drop('Fund Name', axis=1)

    arg

    l2 = df1.columns.values.tolist()
    len(l2)

    l2[0]
    df1

    l1 = []
    sum_of_squares = 0
    for j in range(len(l2)):
        sum_of_squares = 0
        for i in range(len(df)):
            sum_of_squares += df[l2[j]][i] ** 2
            # print(sum_of_squares)
            l1.append(sum_of_squares)

    l3 = []
    import math

    for i in l1:
        l3.append(math.sqrt(i))

    l3
    for i in range(len(l2)):
        for j in range(len(df1)):
            (df1[l2[i]][j]) = (df1[l2[i]][j]) / (l3[i])

    df1

    weights = []
    l=len(arg[2])
    k = 0
    p = 0
    for j in range(l):

        if(j%2==0):
            weights.append(int((sys.argv[2])[j]))
        elif ((sys.argv[2])[j] == ','):
            k = k + 1
        else:
            p=p+1

    if (k != 4 or p>0):
        print("delimeters passed in weights is not ,")
        error=error+1

    wl=len(weights)
    if(wl!=len(l2)):
        print("weights length does not match the column length from 2nd to last")
        error=error+1
    for i in range(len(l2)):
        for j in range(len(df1)):
            df1[l2[i]][j] = df1[l2[i]][j] * weights[i]

    impacts = []
    k = 0
    p=0
    l=len(arg[3])
    for j in range(l):

        if (j % 2 == 0):
            if(arg[3][j]=='+' or arg[3][j]=='-'):
                impacts.append((sys.argv[3])[j])
        elif ((sys.argv[3])[j] == ','):
            k = k + 1
        else:
            p = p + 1
    if (k != 4 or p>0):
        print("delimeters passed in impacts are not ,")
        error = error + 1

    il=len(impacts)
    if(il!=len(l2)):
        print("impacts length does not match the column length from 2nd to last")
        error=error+1
    ideal_best = []
    ideal_worst = []
    for i in range(len(l2)):
        minValue = df1[l2[i]].min()
        maxValue = df1[l2[i]].max()
        if (impacts[i] == '+'):
            ideal_best.append(maxValue)
            ideal_worst.append(minValue)
        else:
            ideal_best.append(minValue)
            ideal_worst.append(maxValue)

    # print(ideal_worst)
    # print(ideal_best)

    distance_worst = []
    distance_best = []
    k = 0
    for i in range(len(df1)):
        sum = 0
        sum1 = 0
        for j in range(len(l2)):
            sum = sum + (ideal_best[j] - df1[l2[j]][i]) ** 2
            sum1 = sum1 + (ideal_worst[j] - df1[l2[j]][i]) ** 2

        sum = math.sqrt(sum)
        sum1 = math.sqrt(sum1)
        distance_best.append(sum)
        distance_worst.append(sum1)

    # distance_best
    # distance_worst
    distance_sum = []
    for i in range(len(df1)):
        distance_sum.append(distance_best[i] + distance_worst[i])

    distance_sum

    p = []
    for i in range(len(df1)):
        p.append(distance_worst[i] / distance_sum[i])

    df1['score'] = p
    df1['Rank'] = df1['score'].rank(ascending=False)
    if(error==0):
        df1.to_csv(arg[4], index=False)


    if(error>0):
        print("program executed unsucessfully")

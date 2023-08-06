import pandas as pd
import math
import sys
class topsis:
  def error_handling(self):
    try:
      a = 5
      b = len(sys.argv)
      assert a == b
    except AssertionError:
      print("Not correct Number of parameters exceeded ")
      sys.exit()
    try:
      f = open(sys.argv[1])
    except FileNotFoundError:
      print('Input File does not exist')
      sys.exit()

    filename = sys.argv[1]
    if filename.endswith(".csv"):
      return filename
    raise ValueError("Input File Extension must be .csv ")

    try:
      df = pd.read_csv(sys.argv[1])
      a = len(df.columns)
      assert a >= 3
    except AssertionError:
      print("Input File must contain 3 or more columns")
      sys.exit()
    try:
      temp = sys.argv[3]
      impact = list(temp.split(","))
      a=len(impact)
      temp = sys.argv[2]
      weight = list(temp.split(","))
      c=len(weight)
      df = pd.read_csv(sys.argv[1])
      b = len(df.columns[1:])
      assert (a==b==c)
    except AssertionError:
      print("Number of Impacts,Number of Weights and Number of columns(2nd to last) must be equal ")
      sys.exit()

    try:
      flag=1
      if ',' in sys.argv[2]:
        flag=0
      assert flag == 0
    except AssertionError:
      print("Weight must be seperated with comma")
      sys.exit()

    try:
      flag=1
      if ',' in sys.argv[3]:
        flag=0
      assert flag == 0
    except AssertionError:
      print("Impact must be seperated with comma")
      sys.exit()
    try:
      temp = sys.argv[3]
      impact = list(temp.split(","))
      flag = 1
      for x in impact:
        if (x == '+' or x == '-'):
          flag = 0
        else:
          flag = 1

      assert flag == 0
    except AssertionError:
      print("Impact must contain +ve or -ve")
      sys.exit()

    try:
        df = pd.read_csv(sys.argv[1])
        df = df.iloc[:,1:len(df)]
        temp=df.dtypes
        flag = 1
        for i in temp:
            if (i=='int64' or i=='float64'):
                flag = 1
            else:
                flag = 0
                break
        assert flag == 1
    except AssertionError:
        print("input file columns(2nd to last) must numeric values only")
        sys.exit()




  def calculation(self):

    df=pd.read_csv(sys.argv[1])
    temp = sys.argv[2]
    w = list(temp.split(","))
    w = [float(i) for i in w]
    temp = sys.argv[3]
    impacts = list(temp.split(","))
    df1=pd.DataFrame()
    x = df.iloc[:, 1:6]

    # Root of sum of squares
    rosos = []
    for i in range(0, x.shape[1]):
      sum = 0
      for j in range(0, x.shape[0]):
        sum += pow(x.loc[j].iat[i], 2)
      fin = pow(sum, 0.5)
      rosos.append(fin)

    for i in range(0, x.shape[1]):
      for j in range(0, x.shape[0]):
        x.loc[j].iat[i] = (x.loc[j].iat[i]) / rosos[i]

    weights_final = []
    for i in range(len(w)):
      weights_final.append(int(w[i]))

    for i in range(0, x.shape[1]):
      for j in range(0, x.shape[0]):
        x.loc[j].iat[i] = (x.loc[j].iat[i]) * weights_final[i]

    # + -> Max is best
    # - -> Min is best
    vj_plus = []  # Ideal best
    vj_minus = []  # Ideal worst
    for i in range(0, x.shape[1]):
      if (impacts[i] == '+'):
        vj_plus.append(x.iloc[:, i].max())
        vj_minus.append(x.iloc[:, i].min())
      else:
        vj_plus.append(x.iloc[:, i].min())
        vj_minus.append(x.iloc[:, i].max())

    si_plus = []
    for i in range(0, x.shape[0]):
      sum = 0
      for j in range(0, x.shape[1]):
        sum += pow(((x.loc[i].iat[j]) - (vj_plus[j])), 2)
      fin = pow(sum, 0.5)
      si_plus.append(fin)

    si_minus = []
    for i in range(0, x.shape[0]):
      sum = 0
      for j in range(0, x.shape[1]):
        sum += pow(((x.loc[i].iat[j]) - (vj_minus[j])), 2)
      fin = pow(sum, 0.5)
      si_minus.append(fin)

    si = []
    for i in range(len(si_plus)):
      si.append(si_plus[i] + si_minus[i])

    pi = []
    for i in range(len(si_plus)):
      pi.append(si_minus[i] / si[i])

    df["Topsis Score"] = pi

    df["Rank"] = df["Topsis Score"].rank(ascending=True)
    df.to_csv(sys.argv[4], index=False)

obj=topsis()
obj.error_handling()
obj.calculation()

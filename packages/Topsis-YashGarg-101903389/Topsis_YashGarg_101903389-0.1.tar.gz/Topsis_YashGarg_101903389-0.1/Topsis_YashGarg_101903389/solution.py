import pandas as pd
import math as m
import sys

def main():
    if len(sys.argv)!=5 :
         raise Exception("Number of parameter are incorrect")
    if sys.argv[1].endswith(('.csv')):
         pass
    else:
         raise Exception("File type must be .csv")
    fn=sys.argv[1]
    
    try:
            df=pd.read_csv(fn)
    except:
            print("No such file is present")
            sys.exit()

    wgts = sys.argv[2]
    ipts = sys.argv[3]
    rt=sys.argv[4]
    
    for i in  ipts:
                
            if i =='+' or i=='-' or ',':
                pass
            else:
                raise Exception("Only positive and negative values are accepted")
       
    topsis(df,wgts,ipts,rt)

def topsis(data, Wgts, Imp,rt):
    

    dtst = data
    X = dtst.iloc[:, 1:].values
    X = X.astype(float)

    W = []
    ipt = []
    for i in Wgts:
      if i != ',': W.append(float(i))
    for i in Imp:
      if i != ',': ipt.append(i)

    a, b, c, d = 0, 0, 0, 0
    for i in range(len(X)):
      a += X[i][0] * X[i][0]
      b += X[i][1] * X[i][1]
      c += X[i][2] * X[i][2]
      d += X[i][3] * X[i][3]
    a = float(m.sqrt(a))
    b = float(m.sqrt(b))
    c = float(m.sqrt(c))
    d = float(m.sqrt(d))

    for i in range(len(X)):
      for j in range(len(X[0])):
        if j == 0: X[i][j] /= a
        elif j == 1: X[i][j] /= b
        elif j == 2: X[i][j] /= c
        elif j == 3: X[i][j] /= d

    for i in range(len(X)):
      for j in range(len(X[0])):
        if j == 0: X[i][j] *= W[0]
        elif j == 1: X[i][j] *= W[1]
        elif j == 2: X[i][j] *= W[2]
        elif j == 3: X[i][j] *= W[3]

    vj_p = []
    vj_m = []
    for j in range(len(X[0])):
      mn=1000
      mx=-1
      for i in range(len(X)):
        mn = min(mn, X[i][j])
        mx = max(mx, X[i][j])
      if (ipt[j] == '+'):
        vj_p.append(mx)
        vj_m.append(mn)
      else:
        vj_p.append(mn)
        vj_m.append(mx)

    Sj_plus = []
    Sj_minus = []
    for i in range(len(X)):
      sum1, sum2 = 0, 0
      for j in range(len(X[0])):
        sum1 += (X[i][j] - vj_p[j]) ** 2
        sum2 += (X[i][j] - vj_m[j]) ** 2
      Sj_plus.append(m.sqrt(sum1))
      Sj_minus.append(m.sqrt(sum2))

    tp_s = []
    for i in range(len(Sj_plus)):
      tp_s.append(Sj_minus[i] / (Sj_plus[i] + Sj_minus[i]))

    dtst["Topsis Score"] = tp_s
    dtst["Rank"] = dtst["Topsis Score"].rank(ascending= False) 
    dtst.sort_values("Topsis Score", inplace = True)
    dtst = dtst.sort_index(axis=0)
    dtst.to_csv(rt,index=False)
    # print(dtst)

if __name__ == "__main__":
    main()
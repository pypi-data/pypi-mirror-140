import pandas as pd
import sys

def main():
  if len(sys.argv) != 5:
      exit()
      
  infile = sys.argv[1]
  try:
      topsis = pd.read_csv(infile)
  except FileNotFoundError:
    exit()

  s = topsis.copy(deep = True)
  n = topsis.shape[0]
  m = topsis.shape[1]
  if m<3:
    exit()

  d = ((topsis.iloc[:,1:] ** 2).sum()) ** 0.5
  for i in range(n):
    s.iloc[i,1:] = s.iloc[i,1:] / d

  weights=sys.argv[2]
  w=weights.split(",")
  impact=sys.argv[3]
  im=impact.split(",")
  if len(im)!=m-1:
      exit()
  if len(w)!=len(im):
    exit()
  output=sys.argv[4]
  for i in range(m-1):
      s.iloc[:,i+1] = s.iloc[:,i+1] * float(w[i])
  vp = []
  vn = []
  for i in range(m-1):
      if im[i]=="+":
        vp.append(s.iloc[:,i+1].max())
        vn.append(s.iloc[:,i+1].min())
      elif im[i]=="-":
        vp.append(s.iloc[:,i+1].min())
        vn.append(s.iloc[:,i+1].max())
      else:
        exit()

  sp = []
  for i in range(n):
      sp.append((((s.iloc[i,1:] - vp) ** 2).sum()) ** 0.5 )

  sn = []
  for i in range(n):
      sn.append((((s.iloc[i,1:] - vn) ** 2).sum()) ** 0.5 )

  p = []
  for i in range(n):
    p.append(sn[i] / (sn[i] + sp[i]))
  topsis['Topsis Score'] = p
  topsis['Rank'] = topsis['Topsis Score'].rank(ascending = 0)
  print(topsis)
  topsis.to_csv(output)
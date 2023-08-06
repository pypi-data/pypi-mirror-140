def topsis(args):
    import pandas as pd
    from math import sqrt
    import os
    if len(args) != 5:
      print('Incorrect number of arguments passed\n')
      exit(0)
      
    if not os.path.isfile(args[1]):
      print('File not found\n')
      exit(0)
      
    if args[1][-4:] != '.csv':
      print('Filetype mismatched\n')
      exit(0)
      
    if args[4][-4:]!='.csv':
      print('Output filetype incorrect')
      exit(0)
    
    df = pd.read_csv(args[1])
    df2 = pd.read_csv(args[1])
    
    if False in df.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all()):
        print('Incorrect data entered')
    
    if len(df.columns) < 3:
        print('Insufficient number of columns')
        exit(0)
    
    weights = args[2]
    impact = args[3]
    
    for c in weights:
      if not(c.isnumeric() or c==','):
        print('Incorrect weights entered\n')
        exit(0)
    
    for c in impact:
      if not(c=='+' or c=='-' or c==','):
        print('Incorrect impacts entered\n')
        exit(0)
    
    weights = weights.split(',')
    weights = list(map(int, weights))
    impact = impact.split(',')
    
    if len(weights) != len(df.columns) - 1:
        print('Incorrect weights entered')
    if len(impact) != len(df.columns) - 1:
        print('Incorrect impacts entered')
    
    x = list(df.columns)
    x.pop(0)
    
    count = 0
    for i in x:
        z = sqrt(sum(list(df[i]**2)))
        df2[i] = (df[i]/z)*weights[count]
        count += 1
    
    best = []
    worst = []
    count = 0
    for i in x:
        if impact[count] == '+':
            best.append(max(df2[i]))
            worst.append(min(df2[i]))
        else:
            best.append(min(df2[i]))
            worst.append(max(df2[i]))
            
    spos = []
    sneg = []
    df2 = df2.iloc[:, 1:]
    df2 = df2.to_numpy()
    for i in range(0,len(df.index)):
        spos.append(sqrt(sum((df2[i] - best)**2)))
        sneg.append(sqrt(sum((df2[i] - worst)**2)))
    perform = [i + j for i, j in zip(sneg, spos)]
    perform = [i / j for i, j in zip(sneg, perform)]
    df['Topsis Score'] = perform
    df['Ranks'] = len(df.index)-(df['Topsis Score'].argsort().argsort())
    
    df.to_csv(args[4], index=False)

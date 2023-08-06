import pandas as pd
import sys
import numpy as np
import logging

def topsis_score(fname,w,im,outfile):
    logging.basicConfig(filename="101903244-log.log",level = logging.DEBUG,encoding='utf-8')

    if ',' not in w:
        logging.error("Array weights should be separated by ','")
        return
    
    weights = w.split(',')
    try:
        weights = list(map(int,weights))
    except ValueError:
        logging.error("Weights has non integral value")
        return

    if ',' not in im:
        logging.error("Array impacts should be separated by ','")
        return
    impact = im.split(',')
    
    # outfile = args[4]
    
    for x in impact:
        if x != '+' and x != '-':
            logging.error("Impact must contain only '+' or '-'")
            return

    try:
        df = pd.read_csv(fname)
    except FileNotFoundError:
        logging.error("Input file provided not found")
        return

    
    if(len(df.columns) < 3):
        logging.error("Less Number of columns in Input File")
        return

    ndf = df.drop('Fund Name', axis=1)
    row = len(ndf)
    cols = len(ndf.iloc[0,:])

    for i in range(row):
        rows = list(ndf.iloc[i])
        for j in range(cols):
            try:
                rows[j] = pd.to_numeric(rows[j])
            except ValueError:
                logging.warning(f"Non numeric value encountered in input.csv at {i}th row and {j}th coln")


    if(cols != len(weights) or cols != len(impact)):
        logging.error("Length of inputs not match.")
        return

    den = ndf.apply(np.square).apply(np.sum,axis = 0).apply(np.sqrt)

    for i in range(cols):
        for j in range(row):
            ndf.iat[j, i] = (ndf.iloc[j, i] / den[i]) * weights[i]

    ideal_best = (ndf.max().values)
    ideal_worst = (ndf.min().values)
    for i in range(cols):
        if impact[i] == '-':
            ideal_best[i], ideal_worst[i] = ideal_worst[i], ideal_best[i]

    score = []
    for i in range(row):
        p,n = 0, 0
        for j in range(cols):
            p += (ideal_best[j] - ndf.iloc[i, j])**2
            n += (ideal_worst[j] - ndf.iloc[i, j])**2
        p, n = p**0.5, n**0.5
        score.append(n/(p + n))

    df['Topsis Score'] = score
    df['Rank'] = (df['Topsis Score'].rank(method='max', ascending=False))
    df.to_csv(outfile)



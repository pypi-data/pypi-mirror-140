import pandas as pd

csv_path = 'data/ibkrcontfutgc5mins.csv'
paths = ['data/ibkrcontfutgc5mins1.csv',
    'data/ibkrcontfutgc5mins2.csv',
    'data/ibkrcontfutgc5mins3.csv',
    'data/ibkrcontfutgc5mins4.csv',
    'data/ibkrcontfutgc5mins5.csv',
    'data/ibkrcontfutgc5mins6.csv',
    'data/ibkrcontfutgc5mins7.csv',
    'data/ibkrcontfutgc5mins8.csv',
    'data/ibkrcontfutgc5mins9.csv',
    'data/ibkrcontfutgc5mins10.csv',
    'data/ibkrcontfutgc5mins11.csv',
    'data/ibkrcontfutgc5mins12.csv',
    'data/ibkrcontfutgc5mins13.csv',
    'data/ibkrcontfutgc5mins14.csv',
    'data/ibkrcontfutgc5mins15.csv']

df = pd.DataFrame()
for path in paths:
    temp = pd.read_csv(path)
    df = df.append(temp)

df = df.drop_duplicates(['tic','date'])
df = df.sort_values(by=['tic','date'])
df.to_csv(csv_path,index=False)
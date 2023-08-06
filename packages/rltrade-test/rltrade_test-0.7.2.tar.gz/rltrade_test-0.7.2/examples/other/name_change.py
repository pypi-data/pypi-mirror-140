import pandas as pd

csv_path = 'data/ibkrcontfutgc5mins.csv' # path with .csv extension

ticker_list = ['GC']
sec_types = ['CONTFUT']
exchanges = ['NYMEX']

ticker_list2 = ['GOLD']
sec_types2 = ['-']
exchanges2 = ['-']

df = pd.read_csv(csv_path)

for i in range(len(ticker_list)):
    df.loc[df['tic']==ticker_list[i],'tic'] = ticker_list2[i]
    df.loc[df['tic']==ticker_list[i],'sec'] = sec_types2[i]
    df.loc[df['tic']==ticker_list[i],'exchange'] = exchanges2[i]

df = df.sort_values(by=['tic','date'])
df.to_csv(csv_path,index=False)
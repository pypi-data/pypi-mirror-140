import pandas as pd
from rltrade import config
from rltrade.data import load_csv
from rltrade.backtests import get_metrics
from rltrade.models import SmartDayTradeGoldLearnerAgent, SmartDayTradeGoldMainAgent

"""
time_frame - last date available
4h  - '2017-12-01'
1h  - '2020-06-19'
30m - '2021-11-18'
15m - '2021-12-03'
5m -  '2021-10-01'
"""

time_frame = "5m"
train_period = ('2022-01-01','2022-01-15')
test_period = ('2022-01-16','2022-02-09')
start_time = "00:00:00"
end_time = "23:55:00" 

csv_path = 'testdata/ibkrcontfutgc5mins4.csv' # path with .csv extension
path = 'models/daytrades/gold_5m_main'


ticker_list = ['GC']
sec_types = ['CONTFUT']
exchanges = ['NYMEX'] 
trades_per_stock = [6] # max number per day is 24h/time_frame

# tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
# additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

tech_indicators = [
    "open_2_sma",
    # "close_2_tema",
    # "tema",
]

additional_indicators = [
    'max_value_price_10',
    # 'max_value_price_50',
    # 'max_value_price_100',
    # 'max_value_price_500',
    # 'max_value_price_1000',
    # 'min_value_price_10',
]

all_indicators = tech_indicators + additional_indicators

for i,indicator in enumerate(all_indicators):

    print(f"Iteration: {i}")
    save_path = path+"/"+str(i)
    tech_indicator = [indicator] if indicator in tech_indicators else []
    additional_indicator = [indicator] if indicator in additional_indicators else []

    print(tech_indicator,additional_indicator)

    df = load_csv(csv_path) # run the download script first

    env_kwargs = {
        "initial_amount": 17_300, #this does not matter as we are making decision for lots and not money.
        "ticker_col_name":"tic",
        "stop_loss":0.015,
        "take_profit":0.03,
        "max_vix_fix":5,
        "min_vix_fix":0.1,
        "vix_fix_lag":50,
        "lot_size":0.01,
        "target_metrics":['asset','unrealized'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
        "transaction_cost":0.9, #transaction cost per order
        "tech_indicator_list":tech_indicator + additional_indicator, 
        "reward_scaling": 10}

    PPO_PARAMS = {'ent_coef':0.005,
                'learning_rate':0.01,
                'batch_size':288}

    agent = SmartDayTradeGoldLearnerAgent("ppo",
                        df=df,
                        account=None,
                        time_frame=time_frame,
                        ticker_list=ticker_list,
                        sec_types = sec_types,
                        trades_per_stock=trades_per_stock,
                        exchanges=exchanges,
                        ticker_col_name="tic",
                        tech_indicators=tech_indicator,
                        additional_indicators=additional_indicator,
                        train_period=train_period,
                        test_period=test_period,
                        start_time=start_time,
                        end_time=end_time,
                        env_kwargs=env_kwargs,
                        model_kwargs=PPO_PARAMS,
                        tb_log_name='ppo',
                        epochs=2)

    agent.train_model()
    agent.make_prediction() #testing model on testing period
    agent.save_model(save_path) #save the model for trading

##############
# Main model #
##############
df_actions = pd.DataFrame()
for i in range(len(all_indicators)):
    load_path =  path+"/"+str(i)
    df = pd.read_csv(load_path+'/action_df.csv')
    df_actions = df_actions.append(df)
df_actions['date'] = pd.to_datetime(df_actions['date'])
df_actions['only date'] = df_actions['date'].dt.date

main_env_kwargs = {
    "initial_amount": 17_300, #this does not matter as we are making decision for lots and not money.
    "ticker_col_name":"tic",
    "stop_loss":0.01,
    "take_profit":0.03,
    "max_vix_fix":5,
    "min_vix_fix":0.1,
    "vix_fix_lag":50,
    "lot_size":0.01,
    "target_metrics":['asset','unrealized'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":0.9, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 10}

MAIN_PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.01,
            'batch_size':288}
start = df_actions['date'].min()
end = df_actions['date'].max()
date_range = pd.date_range(start=start,end=end,freq='1 Y') 
date_range = [x.strftime('%Y-%m-%d') for x in date_range]

if test_period[1] not in date_range:
    date_range = date_range + [test_period[1]]
print(date_range)

for i in range(len(date_range)-2):

    train_period_ = (date_range[0],date_range[i+1])
    test_period_ = (date_range[i+1],date_range[i+2])

    print("Train Period: ",train_period_)
    print("Test Period: ",test_period_)

    agent = SmartDayTradeGoldMainAgent("ppo",
                            df=df_actions,
                            account=None,
                            time_frame=time_frame,
                            ticker_list=ticker_list,
                            sec_types = sec_types,
                            trades_per_stock=trades_per_stock,
                            exchanges=exchanges,
                            ticker_col_name="tic",
                            tech_indicators=tech_indicators,
                            additional_indicators=additional_indicators,
                            train_period=train_period_,
                            test_period=test_period_,
                            start_time=start_time,
                            end_time=end_time,
                            env_kwargs=env_kwargs,
                            model_kwargs=PPO_PARAMS,
                            tb_log_name='ppo',
                            epochs=2)

    agent.train_model()
    agent.make_prediction()
    agent.save_model(path+"/main")
    get_metrics(path+"/main")
import pandas as pd  
import numpy as np  
import pandas_datareader as pdr
import matplotlib.pyplot as plt  
import datetime 
import yfinance as yf
from nsepy import get_history
from datetime import date
import datetime as dt
from nsetools import Nse
import seaborn as sns  
from nsetools import Nse 
import datetime 
from datetime import datetime, timedelta
from nsepy.history import get_price_list
import pandas_datareader.data as web
from datetime import datetime, timedelta
import datetime

def all_time_high(shrape_look_back_period,freq_day):
    
    # df=pd.read_csv(r"C:\Users\DeepakShenoy\Desktop\Quantitative Research\Short_Sell\equity_data.csv", index_col=0)

    prices = get_price_list(dt=date(2021,4,30))
    prices =prices.loc[prices['SERIES'] == 'EQ']
    condition = prices['TOTTRDVAL'] >25_00_00_000
    prices= prices[condition]

    df=prices.loc[prices['SERIES'] == 'EQ']
    df= df[['SYMBOL']]
    stock_list=list(df.SYMBOL)

    ticker_list=[]

    for i in range(len(stock_list)):
        end='.NS'
        symbol=stock_list[i] + end
        ticker_list.append(symbol)

    print(ticker_list)
    print(f"number of stocks is {len(ticker_list)}")

    start = datetime.datetime(2007, 1, 1)
    end = datetime.datetime(2021, 4, 30)

    close_price = web.DataReader(ticker_list, 'yahoo', start, end)['Adj Close']
    print(close_price)
    df=close_price
    df=df.replace(np.nan,0)

    print(df)

    ###############################################################################################################################
    #PARAMETERS

    """
    SHARPE RATIO
    """
    df_pct=df.pct_change()
    df_pct_sum=df_pct.rolling(window=shrape_look_back_period).sum()
    df_std=df_pct.rolling(window=shrape_look_back_period).std()
    df_sharpe_ratio=df_pct_sum.div(df_std)
    df_sharpe_ratio=df_sharpe_ratio.replace(np.nan, 0)
    # print(df_sharpe_ratio)

    """
    ALL-TIME-HIGH-ALGO
    """

    long_algo=df.shift(1).rolling(window=shrape_look_back_period).max()
    long_algo=long_algo.replace(np.nan,0)
    long_algo_signal=df > long_algo
    long_algo_signal.columns=df.columns
    # print(df.columns)
    # print(long_algo_signal)

###############################################################################################################################
    #TRADING DAYS
    date_set=df.index
    date_set_df=pd.DataFrame(date_set)
    date_set_df.columns=['date']

    date_set_df['trading_day']=0

    for i in range(len(date_set_df)):
        
        if i%freq_day ==0:
            date_set_df['trading_day'].iloc[i]=date_set_df['date'].iloc[i]
           
        else:
            date_set_df['trading_day'].iloc[i]=0
            

    condition=date_set_df['trading_day'] !=0
    date_set_df=date_set_df[condition]

    # print(trading_day)
##################################################################################################################################
#STOCK_LIST

    stock_list=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    for i in range(len(trading_day)):
        df_new=df_sharpe_ratio.copy()
        df_new=df_new.loc[trading_day[i]]
    
        df_new=pd.DataFrame(df_new)
        df_new.columns=['sharpe_ratio']
        df_new['stock']=df_new.index
        df_new=df_new.reset_index(drop=True)
        # print(df_new)

        df_all_time=long_algo_signal.copy()
        df_all_time=df_all_time.loc[trading_day[i]]
        df_all_time=pd.DataFrame(df_all_time)
        df_all_time.columns=['condition']
        df_all_time['stock']=df_all_time.index
        df_all_time=df_all_time.reset_index(drop=True)
        condition=df_all_time['condition'] !=False
        df_all_time=df_all_time[condition]
        # print(df_all_time)

        inner_join = pd.merge(df_new,  df_all_time,  on ='stock',  how ='inner') 
        inner_join=inner_join.sort_values(by='sharpe_ratio', ascending=False)
        inner_join=inner_join['stock']
        inner_join_stock=inner_join[:20]
        inner_join_stock=np.array(inner_join_stock)
        # print(inner_join_stock)
        
        stock_list.append(inner_join_stock)
    

    stock_list=pd.DataFrame(stock_list)
    stock_list=stock_list.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    # # print(stock_list)

    buy_list_df=pd.concat([trading_day, stock_list], axis=1)
    buy_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20']
    buy_list_df=buy_list_df.replace(np.nan,0)
    print(buy_list_df)

    # buy_list_df.to_csv(r"C:\Users\DeepakShenoy\Desktop\Quantitative Research\Equity_Strategy_Backtest\buy_list_df_all_time_high.csv")

    ###################################################################################################################################################################

    """
    Calcaulte the entry price of list of stocks selected by system

    """
    #ENTRY_PRICE_LIST

    price_list_buy=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    for i in range(len(trading_day)):

        df_new=df.copy()
        df_new=df_new.loc[trading_day[i]]
        df_new=pd.DataFrame(df_new)
        df_new.columns=['price']
        df_new['stock']=df_new.index
        df_new=df_new.reset_index(drop=True)

        buy_list_new=buy_list_df.copy()
        buy_list_new=buy_list_new.set_index('date')
        buy_list_new=buy_list_new.loc[trading_day[i]]
        buy_list_new=pd.DataFrame(buy_list_new)
        buy_list_new.columns=['stock']
        buy_list_new=buy_list_new.reset_index(drop=True)

        inner_join = pd.merge(df_new,  buy_list_new,  on ='stock',  how ='inner') 
        inner_join_price=inner_join['price']
        price_list_buy.append(inner_join_price)
        

    price_list_buy=pd.DataFrame(price_list_buy)
    price_list_buy=price_list_buy.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_entry=pd.concat([trading_day, price_list_buy], axis=1)
    price_list_df_entry.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20']
    price_list_df_entry=price_list_df_entry.iloc[:-1]
    price_list_df_entry=price_list_df_entry.replace(np.nan,0)

    print(price_list_df_entry)

    ##############################################################################################################################################################################
    """
    Calculate the exit price of stocks as per generated by system
    """
    #EXIT_PRICE_LIST

    price_list_exit=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    for i in range(len(trading_day)-1):
        
        df_new=df.copy()
        df_new=df_new.loc[trading_day[i+1]]
        df_new=pd.DataFrame(df_new)
        df_new.columns=['price']
        df_new['stock']=df_new.index
        df_new=df_new.reset_index(drop=True)

        buy_list_new=buy_list_df.copy()
        buy_list_new=buy_list_new.set_index('date')
        buy_list_new=buy_list_new.loc[trading_day[i]]
        buy_list_new=pd.DataFrame(buy_list_new)
        buy_list_new.columns=['stock']
        buy_list_new=buy_list_new.reset_index(drop=True)

        inner_join = pd.merge(df_new,  buy_list_new,  on ='stock',  how ='inner') 
        inner_join_price=inner_join['price']
        price_list_exit.append(inner_join_price)

    price_list_exit=pd.DataFrame(price_list_exit)
    price_list_exit=price_list_exit.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_exit=pd.concat([trading_day, price_list_exit], axis=1)
    price_list_df_exit.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20']
    price_list_df_exit['date']=price_list_df_exit['date'].shift(-1)
    price_list_df_exit=price_list_df_exit.iloc[:-1]
    price_list_df_exit=price_list_df_exit.replace(np.nan,0)
    print(price_list_df_exit)

      
# ##################################################################################################################################################################################
    """
    Calculate the month on month return generated by system
    """

    entry_price=price_list_df_entry.copy()
    entry_price=entry_price.drop('date', axis='columns')
    # print(entry_price)

    exit_price=price_list_df_exit.copy()
    exit_price=exit_price.drop('date', axis='columns')
    # print(exit_price)
    
    diff_df=exit_price.sub(entry_price)
    diff_pct=diff_df.div(entry_price)
    diff_pct=diff_pct*(100/20)
    diff_pct=diff_pct*0.01

    absolute_return=diff_pct.sum(axis=1)
    absolute_return=pd.DataFrame(absolute_return)
    absolute_return.columns=['absolute_return']
    absolute_return['absolute_return']=absolute_return['absolute_return'].shift(1)
    trading_day=np.array(trading_day)
    trading_day=pd.DataFrame(trading_day)
    absolute_return['date']=trading_day
    absolute_return=absolute_return.replace(np.nan,0)

    print(absolute_return)

    ####################################################################################################################################################################
#PORTFOLIO_ANALYSIS

    absolute_return['portfolio']=0

    for i in range(len(absolute_return)):

        if i==0:
            absolute_return['portfolio'].iloc[i]=100
        else:
            absolute_return['portfolio'].iloc[i]= absolute_return['portfolio'].iloc[i-1]*(1+absolute_return['absolute_return'].iloc[i] )

    
    absolute_return['date']=pd.to_datetime(absolute_return['date'])

    absolute_return['date']=pd.to_datetime(absolute_return['date'])
    
    absolute_return = absolute_return.set_index(absolute_return['date'])
    
    cagr=(((absolute_return['portfolio'].iloc[-1]/(absolute_return['portfolio'].iloc[0]))**(1/13))-1)*100

    # print(absolute_return)
    plt.plot( absolute_return['portfolio'])
    plt.title("Equity_Curve")
    plt.show()

    window = 50
    Roll_Max_portfolio = absolute_return['portfolio'].rolling(window, min_periods=1).max()
    Daily_Drawdown_portfolio = (absolute_return['portfolio']/Roll_Max_portfolio - 1)*100

    max_return=absolute_return['absolute_return'].max()*(100)
    min_return=absolute_return['absolute_return'].min()*(100)
    
    absolute_return['result'] =np.where( absolute_return['absolute_return'] > 0, 1 ,-1)

    positive_condition=absolute_return['result'] ==1
    absolute_return_positive = absolute_return[positive_condition]
    
    neagtive_condition=absolute_return['result'] == -1
    absolute_return_negative = absolute_return[neagtive_condition]
    
    print(f"max_return is {max_return} ")
    print(f"min_return is {min_return}")
    print(f"No of Positive months is { absolute_return_positive['result'].sum(axis=0)}")
    print(f"No of Negative months is { absolute_return_negative['result'].sum(axis=0)*(-1)}")
    print(f"CAGR is {cagr}")
    print(f"Max Drawdown is  {Daily_Drawdown_portfolio.min()}")

    plt.plot(Daily_Drawdown_portfolio, color="blue", label="PORTFOLIO")
    plt.title("DRAWDOWN")
    plt.legend()
    plt.show()

    print(buy_list_df.iloc[-1])


all_time_high(60,21)
# all_time_high(shrape_look_back_period,freq_day)
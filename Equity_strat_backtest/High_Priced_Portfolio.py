import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import pandas_datareader as pdr
import datetime 
import yfinance as yf
from nsepy import get_history
from datetime import date
import datetime as dt
from nsetools import Nse
# import talib
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm  
from nsetools import Nse 
import datetime 
from datetime import datetime, timedelta
# import pyfolio as pf

def high_priced(freq_day):
    
    df=pd.read_csv(r"C:\Users\DeepakShenoy\Desktop\Quantitative Research\Short_Sell\hp_feb_2021_100cr.csv", index_col=0)
    df=df.replace(np.nan, 0)

    date_set=df.index
    # print(date_data)
    # print(df)

    ###############################################################################################################################
    #TRADING DAYS
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

    ##################################################################################################################################

    #STOCK_LIST

    stock_list=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    for i in range(len(trading_day)):
        df_new=df.copy()
        df_new=df_new.loc[trading_day[i]]
    
        df_new=pd.DataFrame(df_new)
        df_new.columns=['price']
        df_new=df_new.sort_values(by='price',ascending=False)
        
        df_new=df_new[:15]
        list_buy=df_new.index
        stock_list.append(list_buy)


    stock_list=pd.DataFrame(stock_list)
    stock_list=stock_list.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    # print(stock_list)

    buy_list_df=pd.concat([trading_day, stock_list], axis=1)
    buy_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    print(buy_list_df)

    #####################################################################################################################################################################

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

        buy_list_new=buy_list_df.copy()
        buy_list_new=buy_list_new.set_index('date')
        buy_list_new=buy_list_new.loc[trading_day[i]]
        buy_list_new=pd.DataFrame(buy_list_new)
        buy_list_new.columns=['stock']
        buy_list_new['date']=trading_day[i]
        buy_list_new=buy_list_new.set_index('stock')

        live_data=pd.concat([buy_list_new, df_new], axis=1)
        live_data=live_data.dropna()
        live_data=live_data.reset_index(drop=True)
        live_data_price=live_data['price']
        # print(live_data_price)

        price_list_buy.append(live_data_price)
        
    price_list_buy=pd.DataFrame(price_list_buy)
    price_list_buy=price_list_buy.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_entry=pd.concat([trading_day, price_list_buy], axis=1)
    price_list_df_entry.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    price_list_df_entry=price_list_df_entry.iloc[:-1]

    print(price_list_df_entry)

    ##############################################################################################################################################################################
    """
    Calculate the exit price of stocks as per generated by systmem
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

        buy_list_new=buy_list_df.copy()
        buy_list_new=buy_list_new.set_index('date')
        buy_list_new=buy_list_new.loc[trading_day[i]]
        buy_list_new=pd.DataFrame(buy_list_new)
        buy_list_new.columns=['stock']
        buy_list_new['date']=trading_day[i+1]
        buy_list_new=buy_list_new.set_index('stock')

        live_data=pd.concat([buy_list_new, df_new], axis=1)
        live_data=live_data.dropna()
        live_data=live_data.reset_index(drop=True)
        live_data_price=live_data['price']

        price_list_exit.append(live_data_price)

    price_list_exit=pd.DataFrame(price_list_exit)
    price_list_exit=price_list_exit.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_exit=pd.concat([trading_day, price_list_exit], axis=1)
    price_list_df_exit.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    price_list_df_exit['date']=price_list_df_exit['date'].shift(-1)
    price_list_df_exit=price_list_df_exit.iloc[:-1]
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
    diff_pct=diff_pct*(100/15)
    diff_pct=diff_pct*0.01

    absolute_return=diff_pct.sum(axis=1)
    absolute_return=pd.DataFrame(absolute_return)
    absolute_return.columns=['absolute_return']
    absolute_return['absolute_return']=absolute_return['absolute_return'].shift(1)
    trading_day=np.array(trading_day)
    trading_day=pd.DataFrame(trading_day)
    absolute_return['date']=trading_day
    absolute_return=absolute_return.replace(np.nan, 0)
    absolute_return['date']=pd.to_datetime(absolute_return['date'])
    absolute_return=absolute_return.set_index('date')

    print(absolute_return)
    # pf.create_simple_tear_sheet(absolute_return)
# ####################################################################################################################################################################

#PORTFOLIO_ANALYSIS

    absolute_return['portfolio']=0

    for i in range(len(absolute_return)):

        if i==0:
            absolute_return['portfolio'].iloc[i]=100
        else:
            absolute_return['portfolio'].iloc[i]= absolute_return['portfolio'].iloc[i-1]*(1+absolute_return['absolute_return'].iloc[i] )

    
    # absolute_return['date']=pd.to_datetime(absolute_return['date'])
    cagr=(((absolute_return['portfolio'].iloc[-1]/(absolute_return['portfolio'].iloc[0]))**(1/15))-1)*100

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
    print(f"No of positive months is { absolute_return_positive['result'].sum(axis=0)}")
    print(f"No of Negative months is { absolute_return_negative['result'].sum(axis=0)*(-1)}")
    print(f"CAGR is {cagr}")
    print(f"Max Drawdown is  {Daily_Drawdown_portfolio.min()}")

    plt.plot(Daily_Drawdown_portfolio, color="blue", label="PORTFOLIO")
    plt.title("DRAWDOWN")
    plt.legend()
    plt.show()

    

    
high_priced(50)
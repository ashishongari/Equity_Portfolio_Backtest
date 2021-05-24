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
import talib
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm  
from nsetools import Nse 
import datetime 
from datetime import datetime, timedelta

def sharpe_ratio(day, frequency):
    
    """
    Day is a variable which is used to defimne a rolling sharpe ratio, I.E day=30, Moving sharpe ratio of 30 days

    """
    ##############################################################################################################################################

    """
    Define a universe of stock, calculate moving sharpe ratio

    """
    df=pd.read_csv()

    df_pct=df.pct_change()
    df_pct_sum=df_pct.rolling(window=day).sum()
    df_std=df_pct.rolling(window=day).std()
    df_sharpe_ratio=df_pct_sum.div(df_std)
    date_set=df_sharpe_ratio.index
    # print(df_sharpe_ratio)

    date_set=date_set[day:]
    date_set_df=pd.DataFrame(date_set)
    date_set_df.columns=['date']

    date_set_df['trading_day']=0
    # date_set_df=date_set_df.reset_index(drop=True)

########################################################################################################################################################
    """
    Define Buy and exit trading day for system
    """
    for i in range(len(date_set_df)):
        
        if i%frequency ==0:
            date_set_df['trading_day'].iloc[i]=date_set_df['date'].iloc[i]
           
        else:
            date_set_df['trading_day'].iloc[i]=0
            

    condition=date_set_df['trading_day'] !=0
    date_set_df=date_set_df[condition]

    # trading_day=date_set_df['trading_day']
    # trading_day=np.array(trading_day)
    # new_df_sharpe_ratio=df_sharpe_ratio.copy()

    #####################################################################################################################################################

    """
    Define top 15 stocks which have highest sharpe ratio on each trading and rebalance every 15 days according to top 15 rank
    """
    #STOCK_LIST

    stock_list=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    new_df_sharpe_ratio=df_sharpe_ratio.copy()
    # print(new_df_sharpe_ratio)


    for i in range(len(trading_day)):

        new_df_sharpe_ratio=new_df_sharpe_ratio.copy()

        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)
        
        list_stock=new[:14]
       
        new_df=df.copy()
        new_df=df.loc[trading_day[i]]
        new_df=pd.DataFrame(new_df)
        new_df.columns=['price']

        backtest_df=pd.concat([list_stock,new_df], axis=1)
        backtest_df=backtest_df[:15]
        stock_list.append(backtest_df.index)

    stock_list=pd.DataFrame(stock_list)
    trading_day=pd.DataFrame(trading_day)

    buy_list_df=pd.concat([trading_day, stock_list], axis=1)
    buy_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    # print(buy_list_df)

###########################################################################################################################################################################
#GET_LOT_SIZE

    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    nse = Nse()
    lot_size_dict=nse.get_fno_lot_sizes()
    df_lot_size = pd.DataFrame(list(lot_size_dict.items()),columns = ['stock','lot'])
    df_lot_size=df_lot_size[2:]

    for i in range(len(df_lot_size)):
        end='.NS'
        df_lot_size['stock'].iloc[i] = df_lot_size['stock'].iloc[i] +  end

    df_lot_size=df_lot_size.set_index('stock')
    # print(df_lot_size)
    lot_size_list=[]

    for i in range(len(trading_day)):

        buy_list=buy_list_df.copy()
        buy_list=buy_list.set_index('date')
        buy_list=buy_list.loc[trading_day[i]]
        buy_list=pd.DataFrame(buy_list)
        buy_list.columns=['stock']
        buy_list['date']=trading_day[i]
        buy_list=buy_list.set_index('stock')
        
        df_lot_size_new=df_lot_size.copy()
        lot_size_live=pd.concat([buy_list,df_lot_size_new], axis=1)
        lot_size_live=lot_size_live.dropna()
        lot_size_live=lot_size_live.reset_index(drop=True)
        lot_size_live=lot_size_live['lot']

        lot_size_list.append(lot_size_live)
    
    lot_size_list_df=pd.DataFrame(lot_size_list)
    lot_size_list_df=lot_size_list_df.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)

    lot_size_list_df=pd.concat([trading_day, lot_size_list_df], axis=1)
    lot_size_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    # print(lot_size_list_df) 


######################################################################################################################################################################

    """
    Calculate the entry price of list of stocks selected by system

    """
    #ENTRY_PRICE_LIST

    price_list_buy=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    new_df_sharpe_ratio=df_sharpe_ratio.copy()

    for i in range(len(trading_day)):

        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        new =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)
        list_stock=new[:14]

        new_df=df.copy()
        new_df=df.loc[trading_day[i]]
        new_df=pd.DataFrame(new_df)
        new_df.columns=['price']

        backtest_df=pd.concat([list_stock,new_df], axis=1)
        backtest_df=backtest_df[:15]
        
        backtest_df=backtest_df.reset_index(drop=True)

        price_list_buy.append(backtest_df['price'])
        
    price_list_buy=pd.DataFrame(price_list_buy)
    price_list_buy=price_list_buy.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_entry=pd.concat([trading_day, price_list_buy], axis=1)
    price_list_df_entry.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    price_list_df_entry=price_list_df_entry.iloc[:-1]

    # print(price_list_df_entry)

##############################################################################################################################################################################
    """
    Calculate the exit price of stocks as per generated by systmem
    """
    #EXIT_PRICE_LIST

    price_list_exit=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    # trading_day=trading_day[1:len(trading_day)]
    # trading_day=trading_day[1:-1]

    for i in range(len(trading_day)-1):

        exit_list_df=buy_list_df.copy()
        exit_list_df=exit_list_df.set_index('date')
        exit_list_stock_df=exit_list_df.loc[trading_day[i]]
        exit_list_stock_df=np.array(exit_list_stock_df)
        
        exit_list_stock_df=pd.DataFrame(exit_list_stock_df)
        exit_list_stock_df.columns=['stock']
        exit_list_stock_df['date']=trading_day[i+1]
        
        exit_list_stock_df=exit_list_stock_df.set_index('stock')

        exit_price=df.copy()
        exit_price=exit_price.loc[trading_day[i+1]]
        
        backtest_df=pd.concat([exit_list_stock_df,exit_price], axis=1)
        backtest_df=backtest_df.dropna()
        backtest_df.columns=['date','price']
        backtest_df=backtest_df['price']
        backtest_df=backtest_df.reset_index(drop=True)

        price_list_exit.append(backtest_df)

    price_list_exit=pd.DataFrame(price_list_exit)
    price_list_exit=price_list_exit.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_exit=pd.concat([trading_day, price_list_exit], axis=1)
    price_list_df_exit.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    price_list_df_exit['date']=price_list_df_exit['date'].shift(-1)
    price_list_df_exit=price_list_df_exit.iloc[:-1]
    # print(price_list_df_exit)

# # ##################################################################################################################################################################################
#     """
#     Calculate the month on month return generated by system
#     """

    entry_price=price_list_df_entry.copy()
    entry_price=entry_price.drop('date', axis='columns')
    # print(entry_price)

    exit_price=price_list_df_exit.copy()
    exit_price=exit_price.drop('date', axis='columns')
    # print(exit_price)

    lot_size_list_df=lot_size_list_df.copy()
    lot_size_list_df=lot_size_list_df.drop('date', axis='columns')
    # print(lot_size_list_df)
    
    diff_df=exit_price.sub(entry_price)
    diff_pct=diff_df.mul(lot_size_list_df)

    absolute_return=diff_pct.sum(axis=1)
    absolute_return=pd.DataFrame(absolute_return)
    absolute_return.columns=['absolute_return']
    absolute_return['absolute_return']=absolute_return['absolute_return'].shift(1)
    trading_day=np.array(trading_day)
    trading_day=pd.DataFrame(trading_day)
    absolute_return['date']=trading_day

    # absolute_return_net=absolute_return['absolute_return'].sum(axis=0)

    # print(absolute_return_net)
# ####################################################################################################################################################################
# PORTFOLIO_ANALYSIS

    absolute_return['portfolio']=0

    for i in range(len(absolute_return)):

        if i==0:
            absolute_return['portfolio'].iloc[i]=1_00_00_000
        else:
            absolute_return['portfolio'].iloc[i]= absolute_return['portfolio'].iloc[i-1] + (1+absolute_return['absolute_return'].iloc[i] )
    
    absolute_return=absolute_return.set_index('date')

    print(absolute_return)
    # cagr=(((absolute_return['portfolio'].iloc[-1]/(absolute_return['portfolio'].iloc[0]))**(1/13))-1)*100

    window = 12
    Roll_Max_portfolio = absolute_return['portfolio'].rolling(window, min_periods=window).max()
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
    # print(f"CAGR is {cagr}")
    print(f"Max Drawdown is  {Daily_Drawdown_portfolio.min()}")

    plt.plot( absolute_return['portfolio'])
    plt.title("Equity_Curve")
    plt.show()

    plt.plot(Daily_Drawdown_portfolio, color="blue", label="PORTFOLIO")
    plt.title("DRAWDOWN")
    plt.legend()
    plt.show()
    
sharpe_ratio(252, 25)

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

def moving_sharpe_ratio_backtest(sharpe_day, crossover_day, trading_day):
    
    df=pd.read_csv()

###############################################################################################################################
    #PARAMETERS

    """
    SHARPE RATIO
    """
    df_pct=df.pct_change()
    df_pct_sum=df_pct.rolling(window=sharpe_day).sum()
    df_std=df_pct.rolling(window=sharpe_day).std()
    df_sharpe_ratio=df_pct_sum.div(df_std)
    date_set=df_sharpe_ratio.index
    
    date_set=date_set[sharpe_day:]
    date_set_df=pd.DataFrame(date_set)
    date_set_df.columns=['date']
    date_set_df['trading_sharpe_day']=0


    """
    CROSSOVER CALCULATION

    """

    df_crossover=df.rolling(window=crossover_day).mean()
    df_crossover_condition= df >df_crossover
    # df_crossover_condition

###############################################################################################################################
    #TRADING DAYS
    date_set=date_set[sharpe_day:]
    date_set_df=pd.DataFrame(date_set)
    date_set_df.columns=['date']

    date_set_df['trading_day']=0

    for i in range(len(date_set_df)):
        
        if i%trading_day ==0:
            date_set_df['trading_day'].iloc[i]=date_set_df['date'].iloc[i]
           
        else:
            date_set_df['trading_day'].iloc[i]=0
            

    condition=date_set_df['trading_day'] !=0
    date_set_df=date_set_df[condition]


###################################################################################################################################

    """
    Define top 15 stocks which have highest sharpe ratio on each tradinG and also trading above their repective {crossover_day} day and rebalance every 15 days according to top 15 rank
    """
    #STOCK_LIST

    stock_list=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    new_df_sharpe_ratio=df_sharpe_ratio.copy()

    for i in range(len(trading_day)):
        
        new_df_sharpe_ratio=df_sharpe_ratio.copy()

        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new_sharpe =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)

        df_crossover_condition=df_crossover_condition.copy()

        live_crossover=df_crossover_condition.loc[trading_day[i]]
        live_crossover=pd.DataFrame(live_crossover)
        live_crossover.columns=['crossover']
        live_crossover=live_crossover.dropna()

        condition=live_crossover['crossover'] ==True
        live_crossover=live_crossover[condition]

        live_data=pd.concat([new_sharpe, live_crossover], axis=1)
        live_data=live_data.dropna()
        
        live_data=live_data[:15]
        live_data_list=live_data.index

        stock_list.append(live_data_list)

    stock_list=pd.DataFrame(stock_list)
    trading_day=pd.DataFrame(trading_day)

    buy_list_df=pd.concat([trading_day, stock_list], axis=1)
    buy_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    print(buy_list_df)
    

#####################################################################################################################################################################

    """
    Calculate the entry price of list of stocks selected by system

    """
    #ENTRY_PRICE_LIST

    
    price_list_buy=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    
    for i in range(len(trading_day)):
        
        new_df_sharpe_ratio=df_sharpe_ratio.copy()

        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new_sharpe =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)

        df_crossover_condition=df_crossover_condition.copy()

        live_crossover=df_crossover_condition.loc[trading_day[i]]
        live_crossover=pd.DataFrame(live_crossover)
        live_crossover.columns=['crossover']
        live_crossover=live_crossover.dropna()

        condition=live_crossover['crossover'] ==True
        live_crossover=live_crossover[condition]

        live_data=pd.concat([new_sharpe, live_crossover], axis=1)
        live_data=live_data.dropna()
        
        live_data=live_data[:15]
        live_data_list=live_data.index
        live_data_list=pd.DataFrame(live_data_list)
        live_data_list.columns=['stock']
        live_data_list['trading_date']=trading_day[i]
        stock_list_data=live_data_list.set_index('stock')
        # print(stock_list_data)

        live_price=df.copy()
        live_price=live_price.loc[trading_day[i]]
        # print(live_price)
        
        backtest_price=pd.concat([stock_list_data,live_price], axis=1)
        backtest_price.columns=['trading_date','price']
        backtest_price=backtest_price.dropna()
        backtest_price=backtest_price.reset_index(drop=True)

        live_price_data=backtest_price['price']
        price_list_buy.append(live_price_data)


   
    # print(price_list_buy)
         
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

    for i in range(len(trading_day)-1):

        new_df_sharpe_ratio=df_sharpe_ratio.copy()

        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new_sharpe =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)

        df_crossover_condition=df_crossover_condition.copy()

        live_crossover=df_crossover_condition.loc[trading_day[i]]
        live_crossover=pd.DataFrame(live_crossover)
        live_crossover.columns=['crossover']
        live_crossover=live_crossover.dropna()

        condition=live_crossover['crossover'] ==True
        live_crossover=live_crossover[condition]

        live_data=pd.concat([new_sharpe, live_crossover], axis=1)
        live_data=live_data.dropna()
        
        live_data=live_data[:15]
        live_data_list=live_data.index
        live_data_list=pd.DataFrame(live_data_list)
        live_data_list.columns=['stock']
        live_data_list['trading_date']=trading_day[i]
        stock_list_data=live_data_list.set_index('stock')
        # print(stock_list_data)

        live_price=df.copy()
        live_price=live_price.loc[trading_day[i+1]]
        # print(live_price)
        
        backtest_price=pd.concat([stock_list_data,live_price], axis=1)
        backtest_price.columns=['trading_date','price']
        backtest_price=backtest_price.dropna()
        backtest_price=backtest_price.reset_index(drop=True)

        live_price_data=backtest_price['price']
        price_list_exit.append(live_price_data)


    price_list_exit=pd.DataFrame(price_list_exit)
    price_list_exit=price_list_exit.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_exit=pd.concat([trading_day, price_list_exit], axis=1)
    price_list_df_exit.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15']
    price_list_df_exit['date']=price_list_df_exit['date'].shift(-1)
    price_list_df_exit=price_list_df_exit.iloc[:-1]
    # print(price_list_df_exit)


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
    print(absolute_return)

   
####################################################################################################################################################################
#PORTFOLIO_ANALYSIS

    absolute_return['portfolio']=0

    for i in range(len(absolute_return)):

        if i==0:
            absolute_return['portfolio'].iloc[i]=100
        else:
            absolute_return['portfolio'].iloc[i]= absolute_return['portfolio'].iloc[i-1]*(1+absolute_return['absolute_return'].iloc[i] )

    
    absolute_return['date'] = pd.to_datetime(absolute_return['date'])
    absolute_return=absolute_return.set_index('date')

    print(absolute_return)
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

    # Plot the results
    plt.plot(Daily_Drawdown_portfolio, color="blue", label="PORTFOLIO")
    plt.title("DRAWDOWN")
    plt.legend()
    plt.show()

    print(buy_list_df.iloc[-1])


moving_sharpe_ratio_backtest(200,30,15)
# moving_sharpe_ratio_backtest(sharpe_day, crossover_day, trading_day)


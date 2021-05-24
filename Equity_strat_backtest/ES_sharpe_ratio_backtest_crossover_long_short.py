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
import seaborn as sns
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm  
from nsetools import Nse 
import datetime 
from datetime import datetime, timedelta

def sharpe_ratio(sharpe_day, crossover_day, rebalance_day):
    
    df=pd.read_csv(r"C:\Users\DeepakShenoy\Desktop\Quantitative Research\Short_Sell\F&O_data_2020_oct.csv", index_col=0)
    # print(df)
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
        
        if i%rebalance_day ==0:
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
    new_df_sharpe_ratio=df_sharpe_ratio.copy()

    for i in range(len(trading_day)):
        
        ###############LONG_Logic
        new_df_sharpe_ratio=df_sharpe_ratio.copy()
        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new_sharpe =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=False)
        # print(new_sharpe)

        df_crossover_condition=df_crossover_condition.copy()

        live_crossover=df_crossover_condition.loc[trading_day[i]]
        live_crossover=pd.DataFrame(live_crossover)
        live_crossover.columns=['crossover']
        live_crossover=live_crossover.dropna()
        # print(live_crossover)

        condition=live_crossover['crossover'] ==True
        live_crossover=live_crossover[condition]

        live_data_long=pd.concat([new_sharpe, live_crossover], axis=1)
        live_data_long=live_data_long.dropna()
        live_data_long=live_data_long[0:21]
        live_data_long_list=live_data_long.index
        live_data_long_list=pd.DataFrame(live_data_long_list)
        # print(live_data_long_list)

         ###############SHORT_Logic
        new_df_sharpe_ratio=df_sharpe_ratio.copy()
        live_sharpe_ratio=new_df_sharpe_ratio.loc[trading_day[i]]
        live_sharpe_ratio=pd.DataFrame(live_sharpe_ratio)
        live_sharpe_ratio.columns=['sharpe_ratio']
        live_sharpe_ratio=live_sharpe_ratio.dropna()
        new_sharpe =live_sharpe_ratio.sort_values(by='sharpe_ratio', ascending=True)
        # print(new_sharpe)

        df_crossover_condition=df_crossover_condition.copy()

        live_crossover=df_crossover_condition.loc[trading_day[i]]
        live_crossover=pd.DataFrame(live_crossover)
        live_crossover.columns=['crossover']
        live_crossover=live_crossover.dropna()
        # print(live_crossover)

        condition=live_crossover['crossover'] ==False
        live_crossover=live_crossover[condition]

        live_data_short=pd.concat([new_sharpe, live_crossover], axis=1)
        live_data_short=live_data_short.dropna()
        live_data_short=live_data_short[:4]
        live_data_short_list=live_data_short.index
        live_data_short_list=pd.DataFrame(live_data_short_list)
        # print(live_data_short_list)
        
        long_short_list=pd.concat([live_data_long_list,live_data_short_list])
        long_short_list=long_short_list.reset_index(drop=True)
        long_short_list.columns=['stock']
        long_short_list=long_short_list['stock']
        # print(long_short_list)
  
        stock_list.append(long_short_list)


    stock_list=pd.DataFrame(stock_list)
    stock_list=stock_list.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    # print(stock_list)

    buy_list_df=pd.concat([trading_day, stock_list], axis=1)
    buy_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20','stock_21', 'stock_22','stock_23','stock_24','stock_25']
    print(buy_list_df)

###########################################################################################################################################################################
# GET_LOT_SIZE

    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)

    nse = Nse()
    lot_size_dict=nse.get_fno_lot_sizes()
    df_lot_size = pd.DataFrame(list(lot_size_dict.items()),columns = ['stock','lot'])
    df_lot_size=df_lot_size[2:]

    for i in range(len(df_lot_size)):
        end='.NS'
        df_lot_size['stock'].iloc[i] = df_lot_size['stock'].iloc[i] +  end

    # df_lot_size=df_lot_size.set_index('stock')
    # print(df_lot_size)
    lot_size_list=[]

    for i in range(len(trading_day)):

        buy_list=buy_list_df.copy()
        buy_list=buy_list.set_index('date')
        buy_list=buy_list.loc[trading_day[i]]
        buy_list=pd.DataFrame(buy_list)
        buy_list.columns=['stock']
        buy_list['date']=trading_day[i]
        buy_list=buy_list.reset_index(drop=True)
      
        df_lot_size_new=df_lot_size.copy()
        inner_join = pd.merge(buy_list,  df_lot_size_new,  on ='stock',  how ='inner') 
        
        lot_data= inner_join['lot']
    
        lot_size_list.append(lot_data)
    
    lot_size_list_df=pd.DataFrame(lot_size_list)
    lot_size_list_df=lot_size_list_df.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)

    lot_size_list_df=pd.concat([trading_day, lot_size_list_df], axis=1)
    lot_size_list_df.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20','stock_21', 'stock_22','stock_23','stock_24','stock_25']
    lot_size_list_df['stock_22']=(lot_size_list_df['stock_22']*(-1))
    lot_size_list_df['stock_23']=(lot_size_list_df['stock_23']*(-1))
    lot_size_list_df['stock_24']=(lot_size_list_df['stock_24']*(-1))
    lot_size_list_df['stock_25']=(lot_size_list_df['stock_25']*(-1))
    lot_size_list_df=lot_size_list_df.replace(np.nan,0)
    print(lot_size_list_df) 

# ######################################################################################################################################################################

    """
    Calculate the entry price of list of stocks selected by system

    """
#     #ENTRY_PRICE_LIST

    price_list_buy=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
    new_df_sharpe_ratio=df_sharpe_ratio.copy()

    for i in range(len(trading_day)):

        buy_list=buy_list_df.copy()
        buy_list=buy_list.set_index('date')
        buy_list=buy_list.loc[trading_day[i]]
        buy_list=pd.DataFrame(buy_list)
        buy_list.columns=['stock']
        buy_list['date']=trading_day[i]
        buy_list=buy_list.reset_index(drop=True)
        # print(buy_list)

        df_price=df.copy()
        df_price=df_price.loc[trading_day[i]]
        df_price=pd.DataFrame(df_price)
        df_price.columns=['price']
        re_index=df_price.index
        df_price['stock']=re_index
        df_price=df_price.reset_index(drop=True)
        # print(df_price)

        inner_join = pd.merge(buy_list,  df_price,  on ='stock',  how ='inner') 
        # print(inner_join)

        entry_price=inner_join['price']
        price_list_buy.append(entry_price)

        

    price_list_buy=pd.DataFrame(price_list_buy)
    price_list_buy=price_list_buy.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_entry=pd.concat([trading_day, price_list_buy], axis=1)
    price_list_df_entry.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20','stock_21', 'stock_22','stock_23','stock_24','stock_25']
    price_list_df_entry=price_list_df_entry.iloc[:-1]
    price_list_df_entry=price_list_df_entry.replace(np.nan, 0)
    print(price_list_df_entry)

# ##############################################################################################################################################################################
    """
    Calculate the exit price of stocks as per generated by systmem
    """
    #EXIT_PRICE_LIST

    price_list_exit=[]
    trading_day=date_set_df['trading_day']
    trading_day=np.array(trading_day)
  
    for i in range(len(trading_day)-1):
        
        buy_list=buy_list_df.copy()
        buy_list=buy_list.set_index('date')
        buy_list=buy_list.loc[trading_day[i]]
        buy_list=pd.DataFrame(buy_list)
        buy_list.columns=['stock']
        buy_list['date']=trading_day[i+1]
        buy_list=buy_list.reset_index(drop=True)
        # print(buy_list)

        df_price=df.copy()
        df_price=df_price.loc[trading_day[i+1]]
        df_price=pd.DataFrame(df_price)
        df_price.columns=['price']
        re_index=df_price.index
        df_price['stock']=re_index
        df_price=df_price.reset_index(drop=True)
        # print(df_price)

        inner_join = pd.merge(buy_list,  df_price,  on ='stock',  how ='inner') 
        # print(inner_join)

        exit_price=inner_join['price']
        price_list_exit.append(exit_price)

    price_list_exit=pd.DataFrame(price_list_exit)
    price_list_exit=price_list_exit.reset_index(drop=True)
    trading_day=pd.DataFrame(trading_day)
    price_list_df_exit=pd.concat([trading_day, price_list_exit], axis=1)
    price_list_df_exit.columns=['date','stock_1','stock_2','stock_3','stock_4','stock_5','stock_6','stock_7','stock_8','stock_9','stock_10','stock_11','stock_12','stock_13','stock_14','stock_15','stock_16','stock_17', 'stock_18','stock_19','stock_20','stock_21', 'stock_22','stock_23','stock_24','stock_25']
    price_list_df_exit['date']=price_list_df_exit['date'].shift(-1)
    price_list_df_exit=price_list_df_exit.iloc[:-1]
    price_list_buy=price_list_buy.replace(np.nan,0)
    print(price_list_df_exit)

# # # ##################################################################################################################################################################################
    """
    Calculate the month on month return generated by system
    """

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

    print(absolute_return)
# # # ####################################################################################################################################################################
# # PORTFOLIO_ANALYSIS

    absolute_return['portfolio']=0

    for i in range(len(absolute_return)):

        if i==0:
            absolute_return['portfolio'].iloc[i]=1_00_00_000
        else: 
            absolute_return['portfolio'].iloc[i]= absolute_return['portfolio'].iloc[i-1] + (1+absolute_return['absolute_return'].iloc[i] )
    
    absolute_return=absolute_return.set_index('date')

    print(absolute_return)
    cagr=(((absolute_return['portfolio'].iloc[-1]/(absolute_return['portfolio'].iloc[0]))**(1/15))-1)*100

    plt.plot( absolute_return['portfolio'])
    plt.title("Equity_Curve")
    plt.show()

    window = 50
    Roll_Max_portfolio = absolute_return['portfolio'].rolling(window, min_periods=1).max()
    Daily_Drawdown_portfolio = (absolute_return['portfolio']/Roll_Max_portfolio - 1)*100

    max_return=absolute_return['absolute_return'].max()
    min_return=absolute_return['absolute_return'].min()
    
    absolute_return['result'] =np.where( absolute_return['absolute_return'] > 0, 1 ,-1)

    positive_condition=absolute_return['result'] ==1
    absolute_return_positive = absolute_return[positive_condition]
    
    neagtive_condition=absolute_return['result'] == -1
    absolute_return_negative = absolute_return[neagtive_condition]
    
    print(f"max_return is {max_return} ")
    print(f"min_return is {min_return}")
    print(f"No of positive months is { absolute_return_positive['result'].sum(axis=0)}")
    print(f"No of Neagtive months is { absolute_return_negative['result'].sum(axis=0)*(-1)}")
    print(f"CAGR is {cagr}")
    print(f"Max Drawdown is  {Daily_Drawdown_portfolio.min()}")

    plt.plot(Daily_Drawdown_portfolio, color="blue", label="PORTFOLIO")
    plt.title("DRAWDOWN")
    plt.legend()
    plt.show()

    # absolute_return.to_csv(r"C:\Users\DeepakShenoy\Desktop\Quantitative Research\Equity_Strategy_Backtest\sharpe_200_crossover_150.csv")

    return 

sharpe_ratio(100, 100, 21)

# def sharpe_ratio(sharpe_day, crossover_day)

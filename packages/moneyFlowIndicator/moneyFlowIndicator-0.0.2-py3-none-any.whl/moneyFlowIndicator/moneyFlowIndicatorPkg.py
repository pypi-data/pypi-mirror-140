class mf_movement():
    
    def __init__(self):
        import pandas as pd
        self.keeper = 'tbd'
        self.num_days = 115 #number of days for rolling average; used in line 60
        self.days_back = 200 #number of days to go back from today to collect data. line 152
        self.df_summary_table = pd.DataFrame(columns = ['n', 'Static_Profit', 'Dynamic_Profit', 'Dynamic_Over_Static'])
        self.n = 0
        self.begin_shares = 1
    
    def obj_to_date(self, df):
        import pandas as pd
        df['Date'] = pd.to_datetime(df['Date'])
        
    def cmf(self, df):
        df['pre_cmf'] = (df['close_low'] - df['high_close']) * df['Volume']
        df['cmf'] = df['pre_cmf'].rolling(self.num_days).sum() / df['Volume'].rolling(self.num_days).sum()
        return df
    
    def differences(self, df):
        df['high_low'] = df['High'] - df['Low']
        df['open_close'] = df['Open'] - df['Close']
        df['open_high'] = df['Open'] - df['High']
        df['open_low'] = df['Open'] - df['Low']
        df['high_close'] = df['High'] - df['Close']
        df['close_low'] = df['Close'] - df['Low']
        return df    
    
    def yahoo_api(self):
        import pandas as pd
        import yfinance as yf
        from datetime import datetime, timedelta

        #symbol = input('What is the stock symbol? ')
        symbol = 'cost'
        #print('The symbol is: ', symbol)
        end_date = datetime.now()       
        d = timedelta(days = self.days_back) #you are getting self.days_back records (first self.num_days dropped when calculated 20 simple moving average.)
        a = end_date - d # goes back self.days_back
        end_date = end_date.strftime('%Y-%m-%d') #keeps only the date ... removes the time stamp
        begin_date = a.strftime('%Y-%m-%d')

        df = yf.download(symbol,
        start = begin_date,
        end = end_date,
        progress = False)
        return df
        
    def buy_sell_signals(self, df1):
        # Steps through the dataframe in groups of 206 on record at a time to find the buy sell indicators of the most
        # recent day.
        # dfBuySell is the dataframe that holds the dates when there is a either a buy or sell signal

        mf = mf_movement() #Instantiates the class
        import pandas as pd
        
        df2Temp = df1.copy()

        dfBuySell = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Buy_Sell'])
                      
        if (df2Temp.iloc[-6, 13] < df2Temp.iloc[-5, 13]
            and df2Temp.iloc[-5, 13] < df2Temp.iloc[-4, 13] 
            and df2Temp.iloc[-4, 13] < df2Temp.iloc[-3, 13]
            and df2Temp.iloc[-3, 13] < df2Temp.iloc[-2, 13]
            and df2Temp.iloc[-2, 13] > df2Temp.iloc[-1, 13]):

            dfBuySellTemp = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Buys_Sell'])
            dfBuySellTemp = df2Temp.iloc[-1, 0:5]
            dfBuySellTemp['Buy_Sell'] = 'Sell'
            dfBuySell = dfBuySell.append(dfBuySellTemp)
            dfBuySell = dfBuySell.reindex()
            del dfBuySellTemp

        elif (df2Temp.iloc[-6, 13] > df2Temp.iloc[-5, 13]
            and df2Temp.iloc[-5, 13] > df2Temp.iloc[-4, 13] 
            and df2Temp.iloc[-4, 13] > df2Temp.iloc[-3, 13]
            and df2Temp.iloc[-3, 13] > df2Temp.iloc[-2, 13]
            and df2Temp.iloc[-2, 13] < df2Temp.iloc[-1, 13]):

            dfBuySellTemp = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Buys_Sell'])
            dfBuySellTemp = df2Temp.iloc[-1, 0:5]
            dfBuySellTemp['Buy_Sell'] = 'Buy'        
            dfBuySell = dfBuySell.append(dfBuySellTemp)
            dfBuySell = dfBuySell.reindex()
            del dfBuySellTemp

        else:
            dfBuySellTemp = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Buys_Sell'])
            dfBuySellTemp = df2Temp.iloc[-1, 0:5]
            dfBuySellTemp['Buy_Sell'] = 'No Action'        
            dfBuySell = dfBuySell.append(dfBuySellTemp)
            dfBuySell = dfBuySell.reindex()
            del dfBuySellTemp

        del df2Temp
    
        return dfBuySell
    
    def output_signal(self,df1):
        date = df1.index[0].strftime('%Y-%m-%d')
        print('WARNING: This is for illustration and entertainment purposes ONLY.')
        print('Do NOT use this information for anything. This includes but is not limited to any financial ')
        print('decisions, and/or stock, option and/or bond purchases, real estate transactions or any other decision. If you' )
        print('disregard this warning you do so at your sole risk and you assume all responsibility for the consequences.')
        print('By disregarding this warning you also agree that you will indemnify Kokoro Analytics, its officers,')
        print('employees, volunteers, vendors and contractors from any damages incured from disregarding this warning.')
        
        agreement = input('Press enter if you have read and will abide by the "Warning" statement above.')
        
        if not agreement:
            print('\nThe last date is: ', date , '; The signal is: ', df1.iloc[-1, 5])
        
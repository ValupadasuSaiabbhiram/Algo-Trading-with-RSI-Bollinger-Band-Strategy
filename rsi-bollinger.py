#Read data
#Rename and reformat pricing to 2 decimal places 
def read_data(tick_symbol, start_date, end_date):
    data = get_data(tick_symbol, start_date=start_date, end_date=end_date, index_as_date = False)
    data = data.rename(columns={'date':'Date', 'high':'High', 'low':'Low', 'close':'Close', 'adjclose':'Adj Close', 'volume':'Volume'})
    lis = ['High', 'Low', 'Close', 'Adj Close']
    for i in lis:
        data[i] = data[i].round(2)
    return data

#Calculate relative strength of stock in time period (days)
def calculate_relative_strength(data, time_period):
    
    #set date as index
    data = data.set_index(data['Date'])
    
    #create delta
    delta = data['Close'].diff(1)
    
    #create gains and loss variables 
    up = delta.copy()
    down = delta.copy()
    
    #conditional to set delta gain
    up[up < 0] = 0
    down[down > 0] = 0
    
    #get average of gains
    AVG_gain = up.rolling(window = time_period).mean()
    
    #get average of loss
    AVG_loss = abs(down.rolling(window = time_period).mean())
    return (AVG_gain, AVG_loss)

#Calculates RSI
def calculate_RSI(AVG_gain, AVG_loss):
   
    # Calculate relative strength
    RS = AVG_gain/AVG_loss
    
    #Calculate relative strength index
    RSI = 100.0-(100.0/(1.0+RS))
    return RSI

#Plot RSI 
def plot_RSI(RSI, tick_symbol):
    
    #set plot sizes
    plt.figure(figsize=(30,7.5))
    
    #plot RSI values against date index
    plot = sns.lineplot(x = RSI.index, y = RSI.values)
    plot.set_title("RSI: " + tick_symbol)
    plot.set_ylabel('Relative Strength Index')
    
    #plot all levels in RSI
    plot.axhline(30, color = 'green')
    plot.axhline(70, color = 'green')
    plot.axhline(20, color = 'yellow')
    plot.axhline(80, color = 'yellow')
    plot.axhline(10, color = 'red')
    plot.axhline(90, color = 'red')
    
    #Get the last/current RSI
    data = RSI.tail(1)
    
    #If greater than 70, display "Sell"
    if data.values > 70:
        for x,y in zip(data.index,data.values):
            label = "Sell"
            plt.annotate(label, # this is the text
                         (x,y), # this is the point to label
                         textcoords="offset points", # how to position the text
                         xytext=(0,10), # distance from text to points (x,y)
                         ha='center',
                         fontsize = 25) # horizontal alignment can be left, right or center
            plt.scatter(data.index, data.values,label = 'Sell', marker = 'v', color = 'red', alpha = 1, s = 100) #plot scatter on RSI plot
    #If less than 30, display "Buy"
    elif data.values < 30:
        for x,y in zip(data.index,data.values):
            label = "Buy"
            plt.annotate(label, # this is the text
                         (x,y), # this is the point to label
                         textcoords="offset points", # how to position the text
                         xytext=(0,10), # distance from text to points (x,y)
                         ha='center',
                         fontsize = 25) # horizontal alignment can be left, right or center
            plt.scatter(data.index, data.values, label = 'Buy', marker = '^', color = 'green', alpha = 1, s = 100) #plot scatter on RSI plot   

#Combine all smaller elements to single function
def RSI(data, tick_symbol, time_period):
        gain, loss = calculate_relative_strength(data, time_period)
        RSI = calculate_RSI(gain, loss)
        plot_RSI(RSI, tick_symbol)

# Produces the bollinger bands for a stock 
def Bollinger_Band(data, period, ticker):
        plt.figure(figsize=(30,15.5))
        data['bollinger_first'] = data['Close'].rolling(period).mean() 
        #Use formula
        data['bollinger_second'] = data['Close'].rolling(period).mean() + 2*(data['Close'].rolling(period).std())
        data['bollinger_third'] = data['Close'].rolling(period).mean() - 2*(data['Close'].rolling(period).std())
        
        #signal to determine upper and lower band crossovers 
        buy = []
        sell = []
        for i in range(len(data['Close'])):
            if data['Close'][i] > data['bollinger_second'][i]:
                buy.append(np.nan)
                sell.append(data['Close'][i])
            elif data['Close'][i] < data['bollinger_third'][i]:
                buy.append(data['Close'][i])
                sell.append(np.nan)
            else:
                buy.append(np.nan)
                sell.append(np.nan)
    
        #plot result 
        graph = sns.lineplot(data = data, x = 'Date', y = 'Close')
        sns.lineplot(data = data, x = 'Date', y = 'bollinger_second')
        sns.lineplot(data = data, x = 'Date', y = 'bollinger_first')
        sns.lineplot(data = data, x = 'Date', y = 'bollinger_third')
        plt.legend(['Close Price', 'Upper Band', 'Middle Band', 'Lower Bound'])
        graph.set_title("Bollinger Bands:" + tick_symbol)
        
        #create columns for buy and sell signals
        data['Buy'] = buy
        data['Sell'] = sell
        
        #obtain non-null records
        data_buy_non_nan = data.loc[data['Buy'].notnull()]
        data_sell_non_nan = data.loc[data['Sell'].notnull()]
        
        #concatenate signals
        signals = pd.concat([data_buy_non_nan, data_sell_non_nan])
        signals = signals.reset_index(drop = True)
        
        #plot signals 
        plt.scatter(data['Date'], data['Buy'], label = 'Buy', marker = '^', color = 'green', alpha = 1)
        plt.scatter(data['Date'], data['Sell'],label = 'Sell', marker = 'v', color = 'red', alpha = 1)
        
        #Add close price on signals 
        for x,y,z in zip(signals['Date'], signals['Close'], signals['Close']):
            label = z #Label corresponds to labels in dataset
            plt.annotate(label, #text to be displayed
                         (x,y), #point for the specific label
                         textcoords="offset points", #positioning of the text
                         xytext=(0,10), #distance from text to points
                         ha='center',
                         fontsize = 12) #horizontal alignment

#Combine all RSI and Bollinger Band functions into one 
def RSI_Bollinger(data, period_bollinger, period_RSI, ticker):
    fig = plt.figure()
    bollinger = Bollinger_Band(data, period_bollinger, ticker)
    rsi = RSI(data, ticker, period_RSI)
    bollinger
    rsi
    plt.show()

if __name__ == "__main__": 
    #Set status to 'buy' or 'sell' for signal prices
    tick_symbol = input("Ticker Symbol: ")
    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    data = read_data(tick_symbol, start_date, end_date)



    #specify period of days for RSI
    period_RSI = int(input('Time period of RSI (in days)'))
   
    #specify period for bollinger
    period_Boll = int(input('Time period of Bollinger Band (in days)'))
    
    #view results
    RSI_Bollinger(data, period_Boll, period_RSI, tick_symbol)


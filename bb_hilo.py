import numpy as np
import pandas as pd

import pandas_datareader.data as pdr
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

import talib 


'''
Hilo indicator
'''
def hilo(highdf,lowdf,closedf):
    length = 4
    displace = 1
        
    
    highsma = talib.SMA(highdf, length)
    lowsma = talib.SMA(lowdf, length)

    fillzero=np.where(np.isnan(highsma))
    highsma[fillzero]=0
    fillzero=np.where(np.isnan(lowsma))
    lowsma[fillzero]=0
    
    swing = np.where((closedf > np.roll(highsma,displace)),1,0)
    swing = np.where((closedf < np.roll(lowsma,displace)),-1,swing)
    
    ghl = np.zeros(len(closedf))
    swingf = np.zeros(len(closedf))
    
    
    for i in range(1,len(lowsma)):
        if swing[i] == 1:
            low = True
            high = False
            ghl[i]=lowsma[i-1]
            swingf[i]=swing[i]
        elif swing[i] == -1:
            high = True
            low = False
            ghl[i]=highsma[i-1]
            swingf[i]=swing[i]
        else:
            ghl[i]=ghl[i-1]
            swingf[i]=swingf[i-1]
            # if low:
            #     ghl[i]=lowsma[i-1]
            # elif high:
            #     ghl[i]=highsma[i-1]
            
    return swingf,ghl

end_date = datetime(2020,4,1)#datetime.now()#datetime(2019,12,16)#
start_date = end_date - timedelta(days=365)

tickers = ['petr4']

BUY=True   #whether want to check for buying or selling
MAX_BUY=100  # number of stocks
MONEY=5000  # R$5000.00
delta=15  # check only for signal in previous day


# uncomment below if want analyze more stoks
#tickers=['BBAS3','PETR4','CSAN3','LAME4']

# =============================================================================
# tickers=['PETR4', 'ABCB4', 'TIET11', 'ALPA4', 'ABEV3', 'ANIM3',
#         'ARZZ3', 'AZUL4', 'BTOW3', 'B3SA3', 'BRSR6', 'BBSE3', 'BKBR3',
#         'BRML3', 'BRPR3', 'BBDC4', 'BRAP4', 'BBAS3', 'BRKM5', 'BRFS3',
#         'BPAC11', 'CAML3', 'CRFB3', 'CCRO3', 'CMIG4', 'CESP6', 'HGTX3',
#         'CIEL3', 'CGAS5', 'CSMG3', 'CPLE6', 'CSAN3', 'RLOG3', 'CPFE3',
#         'CVCB3', 'CYRE3', 'DIRR3', 'DMMO3', 'DTEX3', 'ECOR3', 'ELET6',
#         'EMBR3', 'ENBR3', 'ENGI11', 'ENEV3', 'EGIE3', 'EQTL3', 'EVEN3',
#         'EZTC3', 'FESA4', 'FLRY3', 'GFSA3', 'GGBR4', 'GOAU4', 'GOLL4',
#         'GRND3', 'GUAR3', 'HAPV3', 'HBOR3', 'HYPE3', 'IGTA3', 'PARD3',
#         'MEAL3', 'GNDI3', 'MYPK3', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3',
#         'KLBN11', 'LIGT3', 'LINX3', 'RENT3', 'LAME4', 'AMAR3', 'LREN3',
#         'MDIA3', 'MGLU3', 'POMO4', 'MRFG3', 'LEVE3', 'BEEF3', 'MOVI3',
#         'MRVE3', 'MULT3', 'ODPV3', 'OMGE3', 'PCAR4', 'BRDT3', 'PRIO3',
#         'PSSA3', 'PTBL3', 'QUAL3', 'RADL3', 'RAPT4', 'RAIL3', 'SBSP3',
#         'SAPR11', 'SANB11', 'STBP3', 'SMTO3', 'SEER3', 'CSNA3', 'SLCE3',
#         'SMLS3', 'SULA11', 'SUZB3', 'TAEE11', 'TGMA3', 'VIVT4', 'TEND3',
#         'TIMP3', 'TOTS3', 'TRPL4', 'TUPY3', 'UGPA3', 'UNIP6', 'USIM5',
#         'VALE3', 'VLID3', 'VULC3', 'WEGE3', 'WIZS3', 'VVAR3', 'VIVA3',
#         'CEAB3', 'YDUQ3', 'COGN3']
# 
# =============================================================================
for t in tickers:
    #print(t)
    df = pdr.DataReader(t+'.SA', data_source='yahoo', start=start_date, end=end_date)
    
    opendf= df['Open']
    closedf= df['Close']
    highdf = df['High']
    lowdf = df['Low']
    volumedf= df['Volume']
    
    dates = df.index.date
    
    period=14
    
    upper,_,low = talib.BBANDS(closedf.squeeze(),period,2,2,1)
    
    swingf,_ = hilo(highdf.squeeze().values,lowdf.squeeze().values,closedf.squeeze().values)
    

    
    bbp = 100*((closedf.squeeze().values - low.squeeze().values)/(upper.squeeze().values - low.squeeze().values))
    
    fillzero=np.where(np.isnan(bbp))
    
    bbp[fillzero]=0
    
    close=closedf.squeeze().values
    
    dbbp=np.gradient(bbp,1)
    
    
    def buy_stock(
        real_movement,
        signal,
        controle,
        initial_money = MONEY,
        max_buy = MAX_BUY,
        max_sell = 100,
    ):
        """
        real_movement = actual movement in the real world
        delay = how much interval you want to delay to change our decision from buy to sell, vice versa
        initial_state = 1 is buy, 0 is sell
        initial_money = 1000, ignore what kind of currency
        max_buy = max quantity for share to buy
        max_sell = max quantity for share to sell
        """
        starting_money = initial_money
        states_sell = []
        states_buy = []
        sell_unitsl = []
        buy_unitsl = []    
        current_inventory = 0
    
        def buy(i, initial_money, current_inventory):
            #print(i,real_movement)
            shares = initial_money // real_movement[i]
            if shares < 1:
                print(
                    'day %d: total balances %f, not enough money to buy a unit price %f'
                    % (i, initial_money, real_movement[i])
                )
            else:
                if shares > max_buy:
                    buy_units = max_buy
                else:
                    buy_units = shares
                initial_money -= buy_units * real_movement[i]
                current_inventory += buy_units
                # print(
                #     'day %d: buy %d units at price %f, total balance %f'
                #     % (i, buy_units, buy_units * real_movement[i], initial_money)
                # )
                buy_unitsl.append(buy_units * real_movement[i]/max_buy)
            return initial_money, current_inventory
    
        for i in range(1,real_movement.shape[0],1):
            state = signal[i]
            stateold = signal[i-1]
            if stateold < 0 and state > 0 and controle[i] < 0:
                initial_money, current_inventory = buy(
                    i, initial_money, current_inventory
                )
                states_buy.append(i)
            elif stateold > 0 and state < 0 :
                if current_inventory == 0:
                        #print('day %d: cannot sell anything, inventory 0' % (i))
                    current_inventory=0
                else:
                    if current_inventory > max_sell:
                        sell_units = max_sell
                    else:
                        sell_units = current_inventory
                    current_inventory -= sell_units
                    total_sell = sell_units * real_movement[i]
                    initial_money += total_sell
                    try:
                        invest = (
                            (real_movement[i] - real_movement[states_buy[-1]])
                            / real_movement[states_buy[-1]]
                        ) * 100
                    except:
                        invest = 0
                    # print(
                    #     'day %d, sell %d units at price %f, investment %f %%, total balance %f,'
                    #     % (i, sell_units, total_sell, invest, initial_money)
                    # )
                    sell_unitsl.append(total_sell/max_sell)
                states_sell.append(i)
        # print(len(states_sell))
        # print(len(states_buy))
        #invest = ((initial_money - starting_money) / starting_money) * 100
        #total_gains = initial_money - starting_money
        return states_buy, states_sell, initial_money, buy_unitsl,sell_unitsl
    
    states_buy, states_sell, total_gains,  bl, sl = buy_stock(close, dbbp,swingf)
    
    
    #backtest - assumes one year of investment how much money would you make
    if BUY and dates[states_buy[-1]]>=(end_date.date()-timedelta(days=delta)):
        total_gains = total_gains+bl[-1]*MAX_BUY - MONEY
        invest = (total_gains/ MONEY) * 100
        print('%s BUY %s %f GAIN %f invest %f'%(t,dates[states_buy[-1]],bl[-1],total_gains,invest)) 
    
    elif not BUY and dates[states_sell[-1]]>=(end_date.date()-timedelta(days=delta)):
        total_gains = total_gains - MONEY
        invest = (total_gains/ MONEY) * 100
        print('%s SELL %s %f GAIN %f invest %f'%(t,dates[states_sell[-1]],sl[-1],total_gains,invest))

#debug oonly
# total_gains = total_gains - MONEY
# invest = (total_gains/ MONEY) * 100
# print('%s GAIN %f invest %f'%(t,total_gains,invest))
        
#uncomment to check buying selling signals on a graph

# fig = plt.figure(figsize = (15,5))
# plt.plot(close, color='r', lw=2.)
# plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
# plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
# plt.title('total gains %f, total investment %f%%'%(total_gains, invest))
# plt.legend()
# plt.show()





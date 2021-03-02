from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .forms import CreateUserForm
from .utils import token_generator
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, UpdateInfoForm
from .models import Stock
from .forms import StockForm, PackageForm
from .fusioncharts import FusionCharts
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries
import time
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objects as go
from plotly.offline import plot
import requests
from alpha_vantage.techindicators import TechIndicators
import datetime
from .models import Ticker
import pandas as pd
import plotly.express as px
import numpy as np

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id=force_text(urlsafe_base64_decode(uidb64))
            user= User.objects.get(pk=id)
            #checks if already activated
            if not token_generator.check_token(user, token):
                messages.info(request, 'Account already activated')
                return redirect('login')
            #Redirects to login after activating
            if user.is_active:
                return redirect('login')
            #Set user to active
            user.is_active = True
            user.save()
            messages.success(request, 'Account is now activated!')
        except Exception as e:
            pass


        return redirect('login')


def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            #Initialize user as inactive
            user.is_active = False
            user.save()
            uidb64=urlsafe_base64_encode(force_bytes(user.pk))
            #Get domain
            domain=get_current_site(request).domain
            #Create token and uidb
            link=reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
            #Create Activation link
            activate_url = 'http://'+domain+link
            email_subject = 'Activate your account!'
            email_body = \
                'Thank you for registering to our app, ' \
                + user.username + \
                '! Please use this link to verify your account:\n ' \
                + activate_url
            #Get User Email
            email = form.cleaned_data.get('email')
            #Create Message
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@example.com',
                [email],
            )
            #Send Email
            email.send(fail_silently=True)
            username = form.cleaned_data.get('username')
            messages.info(request, 'Account was created for ' + username + '. Check your email for an activation link')
            return redirect('../login/')
    context = {'form': form}
    return render(request, 'register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('../')
        else:
            messages.error(request, 'Username or password is incorrect. Or check your email for an activation link.')
            return render(request, 'login.html')
    context = {}
    return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')
    # import requests
    # import json
    # if request.method == 'POST':
    #     ticker = request.POST['ticker']
    #     api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + ticker + "/quote?token=pk_31a9e3d6616e4a5abbfd6c82edabc089")
    #     try:
    #         api = json.loads(api_request.content)
    #     except Exception as e:
    #         api = "Error..."
    #     return render(request, 'dashboard.html', {'api': api})
    # else:
    #     return render(request, 'dashboard.html', {'ticker': "Enter a Ticker Symbol Above..."})

@login_required(login_url='login')
def updateinfo(request):
    form = UpdateInfoForm()
    if request.method == 'POST':
        form = UpdateInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account information has been updated')
            return redirect('../')
    else:
        form = UpdateInfoForm(instance=request.user)
    context = {'form': form}
    return render(request, 'updateinfo.html', context)

def show_stock_graph(request):
    api_key = 'I2CGXL68P1CJ9XNP'
    if request.method == 'POST':
        # If stock ticker entered is found in database
        try:
            # Make ticker entered to uppercase before running database check
            stock = request.POST['stock'].upper()

            # Create Arrays for each stock market data set
            index = []
            open = []
            high = []
            low = []
            close = []

            # Find database record with ticker entered in input field
            Ticker_db = Ticker.objects.get(ticker=stock)

            # Split long string from database by each comma and create array
            open_list = Ticker_db.open.split(",")
            # Delete last item in array since its messed up
            del open_list[-1]
            # Make each item in array into a float number instead of string
            for n in open_list:
                open.append(float(n))

            # Do this for the rest of the data sets
            high_list = Ticker_db.high.split(",")
            del high_list[-1]
            for n in high_list:
                high.append(float(n))

            low_list = Ticker_db.low.split(",")
            del low_list[-1]
            for n in low_list:
                low.append(float(n))

            close_list = Ticker_db.close.split(",")
            del close_list[-1]
            for n in close_list:
                close.append(float(n))

            index_list = Ticker_db.index.split(",")
            del index_list[-1]
            for n in index_list:
                t = pd.to_datetime(str(n))
                timestring = t.strftime('%Y-%m-%d')
                index.append(timestring)

            #outputs last in array which should be the newest
            macd_list = Ticker_db.macd.split(",")
            del macd_list[-1]
            macd = float(macd_list[-1].strip())

            # Create Pandas Dataframe from newly created arrays
            data = pd.DataFrame({'date': index, '1. open': open, '2. high': high, '3. low': low, '4. close': close})
            datetime_index = pd.DatetimeIndex(index)
            df2 = data.set_index(datetime_index)
            df2.drop('date', axis=1, inplace=True)
            df2.index.name = 'date'

            # Create Candlestick graph from newly created dataframe
            def candlestick():
                figure = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df2.index,
                            high=df2['2. high'],
                            low=df2['3. low'],
                            open=df2['1. open'],
                            close=df2['4. close'],
                        )
                    ]
                )
                candlestick_div = plot(figure, output_type='div')
                return candlestick_div

            # Run Data Calculations
            stockName = Ticker_db.stock_name
            sector = Ticker_db.sector
            marketcap = Ticker_db.market_cap
            yearhigh = Ticker_db.year_high
            yearlow = Ticker_db.year_low
            closingprice = close[0]
            currentPrice = close[0]
            previousClosingPrice = close[1]
            priceChange = close[0] - close[1]
            decimalChange = close[0] / close[1]
            PosNegChange = decimalChange - 1
            percentageChange = PosNegChange * 100

            context = {
                'sector': sector,
                'currentPrice': currentPrice,
                'marketcap': marketcap,
                'yearhigh': yearhigh,
                'yearlow': yearlow,
                'closingprice': closingprice,
                'openprice': open[0],
                'highprice': high[0],
                'lowprice': low[0],
                'stock': stock,
                'stockName': stockName,
                'percentageChange': round(percentageChange, 2),
                'previousClosingPrice': previousClosingPrice,
                'priceChange': round(abs(priceChange), 2),
                'candlestick': candlestick(),
                'macd': round(macd, 2),
                'recommendation': Ticker_db.recommendation
            }
            return render(request, 'show_graph.html', context)
        except:
            context = {
                'incorrectString': True,
            }
            return render(request, 'show_graph.html', context)
    else:
        return render(request, 'show_graph.html')

def pricing(request):
    return render(request, 'pricing.html')

def sectorForm(request):
    print(request.POST)
    info = [None, None, None]
    packages = {'Starter' : '1', 'Deluxe' : '2', 'Ultimate': '3'}
    if request.method == 'POST':
        info[0] = request.POST['sector']
        print(info[0])
        if request.POST['package'] == 'starter':
            info[1] = packages['Starter']
        elif request.POST['package'] == 'deluxe':
            info[1] = packages['Deluxe']
        elif request.POST['package'] == 'ultimate':
            info[1] = packages['Ultimate']
        info[2] = 'Includes ' + info[1] + ' tickers supported by our recommendation system'

    print({'info': info})
    return render(request, 'sector_form.html', {'info': info})


@login_required(login_url='login')
def add_stock(request):
    current_user = request.user
    if request.user.is_authenticated:
        users_stocks = Ticker.objects.get(ownedBy=current_user)
        if request.method == 'POST':
            form = StockForm(request.POST or None)

            if form.is_valid():
                form.save()
                messages.success(request, "Stock has been Added!")
                return redirect('add_stock')
        else:
            output = []
            stock = users_stocks
            output.append(stock)
    else:
        return redirect('pricing.html')
    return render(request, 'add_stock.html', {'users_stocks': users_stocks, 'output': output })

@login_required(login_url='login')
def UpdateDatabase(request):
    # I2CGXL68P1CJ9XNP
    # YX9741BHQFXIYA0B
    api_key = 'AYB32JWT41PK80BR'
    tag_list = ['GOOG', 'NOK', 'GME', 'AMC', 'DAL', 'CCL', 'AMZN', 'PLTR', 'AAPL', 'TSLA']
    for f in range(9, 10):
        # Get Daily Historical Stock Data from Alphavantage API
        ts = TimeSeries(key=api_key, output_format='pandas')
        data_ts, meta_data_ts = ts.get_daily(symbol=tag_list[f])

        ts_df = data_ts

        payload = {'function': 'OVERVIEW', 'symbol': tag_list[f], 'apikey': 'I2CGXL68P1CJ9XNP'}
        r = requests.get('https://www.alphavantage.co/query', params=payload)
        r = r.json()

        # Set string variables for each historical stock data set
        openString= ""
        closeString = ""
        highString = ""
        lowString = ""
        indexString = ""

        # Convert opening prices into one long string
        for s in ts_df['1. open'].values:
            openString += str(s) + ", "

        # Convert high prices into one long string
        for s in ts_df['2. high'].values:
            highString += str(s) + ", "

        # Convert low prices into one long string
        for s in ts_df['3. low'].values:
            lowString += str(s) + ", "

        # Convert close prices into one long string
        for s in ts_df['4. close'].values:
            closeString += str(s) + ", "

        # Convert date range into one long string
        for s in ts_df.index.values:
            indexString += str(s) + ", "

        # Grab specific stock data from alphavantage api
        stockName = r['Name']
        sector = r['Sector']
        marketcap = r['MarketCapitalization']
        peratio = r['PERatio']
        yearhigh = r['52WeekHigh']
        yearlow = r['52WeekLow']
        eps = r['EPS']

        # Put closing prices into array for other data calculations like previous closing price etc...
        timeseries = ts_df.to_dict(orient='records')
        closingprice = []
        for k in timeseries:
            closingprice.append(k['4. close'])
        print(ts_df)
        def human_format(num):
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            # add more suffixes if you need them
            return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

        #-----------------------------------------------ema------------------------------------------------------------#
        #calaculate ema
        #save  a original ema value array, each update pull last ema calculate new one save
        #array of closed values with last one being the current day, n = n-day ema to calculate, n<= total close values
        def ema_initial(close, n): #outputs ema array (old->new)
            ema = []
            sma = sum(close[:n])
            ema.append(sma/n)
            for i in range(n, len(close)):
                weight = 2/(1 + n)
                ema.append((close[i] * weight) + (ema[-1] * (1 - weight)))
            print('current days ', n, '- day ema: ', ema[-1])
            return ema

        def macd_initial(twelve, tsix):
            macdArray = []
            #goes in reverse to the the mismatch in lengths of 26-day emas vs 12-day emas
            for i in range(len(tsix) - 1, -1, -1):
                macdArray.append(twelve[i] - tsix[i])

            # reverse the list from (new...older) to (old...newer)
            return [ele for ele in reversed(macdArray)]

        # returns single value, but takes in oldemas [-1] is newest
        def ema_new(oldEmas, close, n):
            weight = 2 / (1 + n)
            newEma = (close * weight) + (oldEmas[-1] * (1 - weight))
            return newEma

        #saving original closing price and reversing it so (old->new) to help with calculations
        closingprice_ema = np.array(closingprice)[::-1]
       # --------------------------------------------------------------------------------------------------------------#

        # Data calculations
        marketcap = int(marketcap)
        marketcap = human_format(marketcap)
        closingprice = closingprice[0:15]
        currentPrice = closingprice[0]
        previousClosingPrice = closingprice[1]
        priceChange = closingprice[0] - closingprice[1]
        decimalChange = closingprice[0] / closingprice[1]
        PosNegChange = decimalChange - 1
        percentageChange = PosNegChange * 100
        print(f, tag_list[f])

        # Updating database
        # If stock is already created in database, update that database
        try:
            test = Ticker.objects.get(ticker=tag_list[f])

            #Convert needed arrays to floats
            ema12_string_array = test.ema12.replace(' ', '').split(",")
            ema26_string_array = test.ema26.replace(' ', '').split(",")
            macd_signal_string_array = test.macd_signal.replace(' ', '').split(",")
            del ema12_string_array[-1]
            del ema26_string_array[-1]
            del macd_signal_string_array[-1]

            day12 = [float(x) for x in ema12_string_array]
            day26 = [float(x) for x in ema26_string_array]
            macdSignalLine = [float(x) for x in macd_signal_string_array]

            #acts as if newest closing value is [-1], calculates new values for the day
            ema12 = str(ema_new(day12, closingprice_ema[-1], 12))
            ema26 = str(ema_new(day26, closingprice_ema[-1], 26))
            macd_string = day12[-1] - day26[-1]
            macd_signal_string = str(ema_new(macdSignalLine, macd_string, 9))
            macd_string = str(macd_string)

            print('Updating ', stockName, '...')
            test.stock_name = stockName
            test.sector = sector
            test.market_cap = marketcap
            test.current_price = currentPrice
            test.previous_closing_price = previousClosingPrice
            test.percentage_change = percentageChange
            test.year_high = yearhigh
            test.year_low = yearlow
            test.price_change = priceChange
            test.close = closeString
            test.open = openString
            test.high = highString
            test.low = lowString
            test.index = indexString
            test.ema12 = test.ema12 + ema12 + ', '
            test.ema26 = test.ema26 + ema26 + ', '
            test.macd = test.macd + macd_string + ', '
            test.macd_signal = test.macd_signal + macd_signal_string + ', '

            #if macd is crossing above signal line buy else sell
            if float(macd_string) > float(macd_signal_string):
                test.recommendation = 'Buy (Hold)'
            else:
                test.recommendation = 'Sell'

            test.save()
            print('Updated: ', stockName)

        # If stock is NOT created in database, Create that database record
        except:
            print("Creating ", stockName, "...")

            #building initial emas should only run if stock doesnt already exist
            day12 = ema_initial(closingprice_ema, 12)
            day26 = ema_initial(closingprice_ema, 26)
            macd = macd_initial(day12, day26)
            macdSignalLine = ema_initial(macd, 9)

            if macd[-1] > macdSignalLine[-1]:
                recommend = 'Buy (Hold)'
            else:
                recommend = 'Sell'

            day12_string = ""
            day26_string = ""
            macd_string = ""
            macdSignalLine_string = ""

            #Converting to string for database
            for s in day12:
                day12_string += str(s) + ", "
            for s in day26:
                day26_string += str(s) + ", "
            for s in macd:
                macd_string += str(s) + ", "
            for s in macdSignalLine:
                macdSignalLine_string += str(s) + ", "

            test = Ticker(ticker=tag_list[f], stock_name=stockName, sector=sector, market_cap=marketcap,
                          current_price=currentPrice, previous_closing_price=previousClosingPrice,
                          percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow,
                          price_change=priceChange, open=openString, close=closeString, high=highString,
                          low=lowString, index=indexString, ema12=day12_string, ema26=day26_string, macd=macd_string,
                          macd_signal=macdSignalLine_string, recommendation=recommend)
            print("Saving ", test.stock_name, " to the Database...")
            test.save()

        # Still trying to get this to work, Having api limitation issues but this
        # makes it run two api calls at a time (update/create a database record) every 100 seconds
        if f % 3 == 0:
            time.sleep(100)
    print("Finished")
    return render(request, 'update_database.html')
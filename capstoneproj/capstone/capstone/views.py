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
        if len(request.POST['stock']) > 2 and len(request.POST['stock']) < 6:
            stock = request.POST['stock']
            ts = TimeSeries(key=api_key, output_format='pandas')
            data_ts, meta_data_ts = ts.get_daily(symbol=stock)

            #ti = TimeSeries(key=api_key, output_format='pandas')
            #data_ti, meta_data_ti = ti.get_daily(symbol=stock)

            ts_df = data_ts
            #ti_df = data_ti

            payload = {'function': 'OVERVIEW', 'symbol': stock, 'apikey': 'YX9741BHQFXIYA0B'}
            r = requests.get('https://www.alphavantage.co/query', params=payload)
            r = r.json()

            def candlestick():
                figure = go.Figure(
                    data=[
                        go.Candlestick(
                            x=ts_df.index,
                            high=ts_df['2. high'],
                            low=ts_df['3. low'],
                            open=ts_df['1. open'],
                            close=ts_df['4. close'],
                        )
                    ]
                )
                candlestick_div = plot(figure, output_type='div')
                return candlestick_div

            stockName = r['Name']
            sector = r['Sector']
            marketcap = r['MarketCapitalization']
            peratio = r['PERatio']
            yearhigh = r['52WeekHigh']
            yearlow = r['52WeekLow']
            eps = r['EPS']

            timeseries = ts_df.to_dict(orient='records')
            closingprice = []
            for k in timeseries:
                closingprice.append(k['4. close'])
            lowprice = []
            for k in timeseries:
                closingprice.append(k['3. low'])
            highprice = []
            for k in timeseries:
                closingprice.append(k['2. high'])
            openprice = []
            for k in timeseries:
                closingprice.append(k['1. open'])
            pricedata = {
                'close': [closingprice],
                'open': [openprice],
                'high': [highprice],
                'low': [lowprice],
            }
            # miscellaneous stuff
            day = datetime.datetime.now()
            day = day.strftime("%A")

            def human_format(num):
                magnitude = 0
                while abs(num) >= 1000:
                    magnitude += 1
                    num /= 1000.0
                # add more suffixes if you need them
                return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

            marketcap = int(marketcap)
            marketcap = human_format(marketcap)
            closingprice = closingprice[0:15]
            currentPrice = closingprice[0]
            previousClosingPrice = closingprice[1]
            priceChange = closingprice[0] - closingprice[1]
            decimalChange = closingprice[0] / closingprice[1]
            PosNegChange = decimalChange - 1
            percentageChange = PosNegChange * 100

            # Pulling from Database
            try:
                currentPrice2 = Ticker.objects.get(ticker=stock).current_price
            except:
                currentPrice2 = 'Doesnt Exist'


            context = {
                'sector': sector,
                'currentPrice2': currentPrice2,
                'marketcap': marketcap,
                'peratio': peratio,
                'yearhigh': yearhigh,
                'yearlow': yearlow,
                'eps': eps,
                'closingprice': closingprice,
                'openprice': openprice,
                'highprice': highprice,
                'lowprice': lowprice,
                'pricedata': pricedata,
                'timeseries': timeseries,
                'stock': stock,
                'day': day,
                'stockName': stockName,
                'currentPrice': currentPrice,
                'percentageChange': round(percentageChange, 2),
                'previousClosingPrice': previousClosingPrice,
                'priceChange': round(abs(priceChange), 2),
                'candlestick': candlestick(),
            }
            return render(request, 'show_graph.html', context)
        else:
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


# @login_required(login_url='login')
# def add_stock(request):
#     if request.method == 'POST':
#         form = StockForm(request.POST or None)
#
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Stock has been Added!")
#             return redirect('add_stock')
#     else:
#
#         ticker = Stock.objects.all()
#         output = []
#         for ticker_item in ticker:
#             api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_31a9e3d6616e4a5abbfd6c82edabc089")
#             try:
#                 api = json.loads(api_request.content)
#                 output.append(api)
#             except Exception as e:
#                 api = "Error..."
#         return render(request, 'add_stock.html', {'ticker': ticker, 'output': output})

# @login_required(login_url='login')
# def delete(request, stock_id):
#
# 	item = Stock.objects.get(pk=stock_id)
# 	item.delete()
# 	messages.success(request, ("Stock Has Been Deleted!"))
# 	return redirect(add_stock)

@login_required(login_url='login')
def UpdateDatabase(request):
    # I2CGXL68P1CJ9XNP
    # YX9741BHQFXIYA0B
    api_key = 'AYB32JWT41PK80BR'
    tag_list = ['GOOG', 'NOK', 'GME', 'AMC', 'DAL', 'CCL']
    for f in range(4, 6):
        ts = TimeSeries(key=api_key, output_format='pandas')
        data_ts, meta_data_ts = ts.get_daily(symbol=tag_list[f])

        ts_df = data_ts

        payload = {'function': 'OVERVIEW', 'symbol': tag_list[f], 'apikey': 'YX9741BHQFXIYA0B'}
        r = requests.get('https://www.alphavantage.co/query', params=payload)
        r = r.json()
        stockName = r['Name']
        sector = r['Sector']
        marketcap = r['MarketCapitalization']
        peratio = r['PERatio']
        yearhigh = r['52WeekHigh']
        yearlow = r['52WeekLow']
        eps = r['EPS']

        timeseries = ts_df.to_dict(orient='records')
        closingprice = []
        for k in timeseries:
            closingprice.append(k['4. close'])
        lowprice = []
        for k in timeseries:
            closingprice.append(k['3. low'])
        highprice = []
        for k in timeseries:
            closingprice.append(k['2. high'])
        openprice = []
        for k in timeseries:
            closingprice.append(k['1. open'])
        pricedata = {
            'close': [closingprice],
            'open': [openprice],
            'high': [highprice],
            'low': [lowprice],
        }
        # miscellaneous stuff
        day = datetime.datetime.now()
        day = day.strftime("%A")

        def human_format(num):
            magnitude = 0
            while abs(num) >= 1000:
                magnitude += 1
                num /= 1000.0
            # add more suffixes if you need them
            return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

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
        try:
            test = Ticker.objects.get(ticker=tag_list[f])
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
            test.save()
            print('Updated: ', stockName)
        except:
            print("Creating ", stockName, "...")
            test = Ticker(ticker=tag_list[f], stock_name=stockName, sector=sector, market_cap=marketcap,
                          current_price=currentPrice, previous_closing_price=previousClosingPrice,
                          percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow,
                          price_change=priceChange)
            print("Saving ", test.stock_name, " to the Database...")
            test.save()

        if f % 2 == 0:
            time.sleep(70)
    print("Finished")
    return render(request, 'update_database.html')
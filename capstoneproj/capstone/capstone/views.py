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
from .models import Ticker as tickerModel
from .models import Sector
from .models import OwnedPackage, StockJSON
import pandas as pd
import plotly.express as px
import numpy as np
from selenium import webdriver
import csv
import yfinance as yf
import random
import json
from alive_progress import alive_bar

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
            # adds a user to package table
            package = OwnedPackage(user=user)
            package.save()
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
            if OwnedPackage.objects.get(user=request.user).packageNum == -1:
                messages.info(request,
                              'Your portfolio does not have an associated package, please select one from below.')
                return redirect('../pricing/')
            else:
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
    #     tickerModel = request.POST['tickerModel']
    #     api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + tickerModel + "/quote?token=pk_31a9e3d6616e4a5abbfd6c82edabc089")
    #     try:
    #         api = json.loads(api_request.content)
    #     except Exception as e:
    #         api = "Error..."
    #     return render(request, 'dashboard.html', {'api': api})
    # else:
    #     return render(request, 'dashboard.html', {'tickerModel': "Enter a tickerModel Symbol Above..."})


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
        # If stock tickerModel entered is found in database
        try:
            # Make tickerModel entered to uppercase before running database check
            stock = request.POST['stock'].upper()
            print(stock)
            # # Create Arrays for each stock market data set
            # index = []
            # open = []
            # high = []
            # low = []
            # close = []
            #
            # # Find database record with tickerModel entered in input field
            # tickerModel_db = tickerModel.objects.get(tickerModel=stock)
            #
            # # Split long string from database by each comma and create array
            # open_list = tickerModel_db.open.split(",")
            # # Delete last item in array since its messed up
            # del open_list[-1]
            # # Make each item in array into a float number instead of string
            # for n in open_list:
            #     open.append(float(n))
            #
            # # Do this for the rest of the data sets
            # high_list = tickerModel_db.high.split(",")
            # del high_list[-1]
            # for n in high_list:
            #     high.append(float(n))
            #
            # low_list = tickerModel_db.low.split(",")
            # del low_list[-1]
            # for n in low_list:
            #     low.append(float(n))
            #
            # close_list = tickerModel_db.close.split(",")
            # del close_list[-1]
            # for n in close_list:
            #     close.append(float(n))
            #
            # index_list = tickerModel_db.index.split(",")
            # del index_list[-1]
            # for n in index_list:
            #     t = pd.to_datetime(str(n))
            #     timestring = t.strftime('%Y-%m-%d')
            #     index.append(timestring)
            #
            # #outputs last in array which should be the newest
            # macd_list = tickerModel_db.macd.split(",")
            # del macd_list[-1]
            # macd = float(macd_list[-1].strip())
            #
            # #Create Pandas Dataframe from newly created arrays
            # data = pd.DataFrame({'date': index, '1. open': open, '2. high': high, '3. low': low, '4. close': close})
            # datetime_index = pd.DatetimeIndex(index)
            # df2 = data.set_index(datetime_index)
            # df2.drop('date', axis=1, inplace=True)
            # df2.index.name = 'date'
            # print(df2)
            stockModel = StockJSON.objects.get(ticker = stock)
            stockInfo = yf.Ticker(stock).info
            print(stockInfo)
            df = pd.read_json(stockModel.info, orient='index')
            print(df)
            # Create Candlestick graph from newly created dataframe
            def candlestick():
                print('test3')
                figure = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df.index,
                            high=df['High'],
                            low=df['Low'],
                            open=df['Open'],
                            close=df['Close'],
                        )
                    ]
                )
                candlestick_div = plot(figure, output_type='div')
                print('test2')
                return candlestick_div

            # Run Data Calculations
            #stockName = stockModel.stock_name
            # sector = stockModel.sector
            # marketcap = stockModel.market_cap
            # yearhigh = stockModel.year_high
            # yearlow = stockModel.year_low
            # closingprice = stockModel.close
            # currentPrice =
            # previousClosingPrice = close[1]
            # priceChange = close[0] - close[1]
            # decimalChange = close[0] / close[1]
            # PosNegChange = decimalChange - 1
            # percentageChange = PosNegChange * 100
            #what is current price
            try:
                summary = stockInfo['longBusinessSummary']
            except:
                summary = 'No summary available'
            context = {
                'sector': stockModel.sector,
                'currentPrice': stockModel.current_price,
                'marketcap': stockModel.market_cap,
                'yearhigh': stockModel.year_high,
                'yearlow': stockModel.year_low,
                'closingprice': stockModel.current_price,
                'openprice': df['Open'][-1],
                'highprice': df['High'][-1],
                'lowprice': df['Low'][-1],
                'stock': stock,
                'stockName': stockModel.stock_name,
                'percentageChange': stockModel.percentage_change,
                'previousClosingPrice': stockModel.previous_closing_price,
                'priceChange': stockModel.price_change, #does need abs
                'candlestick': candlestick(),
                'macd': df['MACD'][-1],
                'recommendation': df['Recommendation'][-1],
                'summary': summary
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
    context = {}
    if request.method == 'POST':
        userPackage = OwnedPackage.objects.get(user=request.user)
        if 'starter_submit' in request.POST:
            if userPackage.packageNum != 0:
                userPackage.packageNum = 0
                messages.success(request, 'Successfully added Starter Package to account')
                userPackage.save()
                return redirect('../')
        elif 'deluxe_submit' in request.POST:
            if userPackage.packageNum != 1:
                userPackage.packageNum = 1
                messages.success(request, 'Successfully added Deluxe Package to account')
                userPackage.save()
                return redirect('../')
        elif 'ultimate_submit' in request.POST:
            if userPackage.packageNum != 2:
                userPackage.packageNum = 2
                messages.success(request, 'Successfully added Ultimate Package to account')
                userPackage.save()
                return redirect('../')

    return render(request, 'pricing.html', {'num': OwnedPackage.objects.get(user=request.user).packageNum})


def sectorPage(request):
    communication_services = Sector.objects.get(sector_name="Communication Services")
    consumer_descretionary = Sector.objects.get(sector_name="Consumer Discretionary")
    consumer_staples = Sector.objects.get(sector_name="Consumer Staples")
    energy = Sector.objects.get(sector_name="Energy")
    financials = Sector.objects.get(sector_name="Financials")
    health_care = Sector.objects.get(sector_name="Health Care")
    industrials = Sector.objects.get(sector_name="Industrials")
    information_technology = Sector.objects.get(sector_name="Information Technology")
    materials = Sector.objects.get(sector_name="Materials")
    real_estate = Sector.objects.get(sector_name="Real Estate")
    utilities = Sector.objects.get(sector_name="Utilities")
    # Consumer Cyclical Top Performing Stocks
    try:
        consumer_cyclical_filter = tickerModel.objects.filter(sector="Consumer Cyclical")
        ccf_q2 = consumer_cyclical_filter.order_by('-percentage_change')[0]
        ccf_q3 = consumer_cyclical_filter.order_by('-percentage_change')[1]
        ccf_q4 = consumer_cyclical_filter.order_by('-percentage_change')[2]
        ccf_set = []
        ccf_set.append(ccf_q2)
        ccf_set.append(ccf_q3)
        ccf_set.append(ccf_q4)
        print(ccf_set)
        ccf_error = "None"
    except:
        ccf_set = []
        ccf_error = "Yes"
    # Consumer Staples Top Performing Stocks
    try:
        consumer_staples_filter = tickerModel.objects.filter(sector="Consumer Defensive")
        cstf_q2 = consumer_staples_filter.order_by('-percentage_change')[0]
        cstf_q3 = consumer_staples_filter.order_by('-percentage_change')[1]
        cstf_q4 = consumer_staples_filter.order_by('-percentage_change')[2]
        cstf_set = []
        cstf_set.append(cstf_q2)
        cstf_set.append(cstf_q3)
        cstf_set.append(cstf_q4)
        print(cstf_set)
        cstf_error = "None"
    except:
        cstf_set = []
        cstf_error = "Yes"
    # Technology Top Performing Stocks
    try:
        technology_filter = tickerModel.objects.filter(sector="Technology")
        tf_q2 = technology_filter.order_by('-percentage_change')[0]
        tf_q3 = technology_filter.order_by('-percentage_change')[1]
        tf_q4 = technology_filter.order_by('-percentage_change')[2]
        tf_set = []
        tf_set.append(tf_q2)
        tf_set.append(tf_q3)
        tf_set.append(tf_q4)
        print(tf_set)
        tf_error = "None"
    except:
        tf_set = []
        tf_error = "Yes"
    # Communication Services Top Performing Stocks
    try:
        communication_services_filter = tickerModel.objects.filter(sector="Communication Services")
        csf_q2 = communication_services_filter.order_by('-percentage_change')[0]
        csf_q3 = communication_services_filter.order_by('-percentage_change')[1]
        csf_q4 = communication_services_filter.order_by('-percentage_change')[2]
        csf_set = []
        csf_set.append(csf_q2)
        csf_set.append(csf_q3)
        csf_set.append(csf_q4)
        print(csf_set)
        csf_error = "None"
    except:
        csf_set = []
        csf_error = "Yes"
    # Communication Services Top Performing Stocks
    try:
        communication_services_filter = tickerModel.objects.filter(sector="Communication Services")
        csf_q2 = communication_services_filter.order_by('-percentage_change')[0]
        csf_q3 = communication_services_filter.order_by('-percentage_change')[1]
        csf_q4 = communication_services_filter.order_by('-percentage_change')[2]
        csf_set = []
        csf_set.append(csf_q2)
        csf_set.append(csf_q3)
        csf_set.append(csf_q4)
        print(csf_set)
        csf_error = "None"
    except:
        csf_set = []
        csf_error = "Yes"
    # Energy Top Performing Stocks
    try:
        energy_filter = tickerModel.objects.filter(sector="Energy")
        ef_q2 = energy_filter.order_by('-percentage_change')[0]
        ef_q3 = energy_filter.order_by('-percentage_change')[1]
        ef_q4 = energy_filter.order_by('-percentage_change')[2]
        ef_set = []
        ef_set.append(ef_q2)
        ef_set.append(ef_q3)
        ef_set.append(ef_q4)
        print(ef_set)
        ef_error = "None"
    except:
        ef_set = []
        ef_error = "Yes"
    # Financials Top Performing Stocks
    try:
        financials_filter = tickerModel.objects.filter(sector="Financial Services")
        ff_q2 = financials_filter.order_by('-percentage_change')[0]
        ff_q3 = financials_filter.order_by('-percentage_change')[1]
        ff_q4 = financials_filter.order_by('-percentage_change')[2]
        ff_set = []
        ff_set.append(ff_q2)
        ff_set.append(ff_q3)
        ff_set.append(ff_q4)
        print(ff_set)
        ff_error = "None"
    except:
        ff_set = []
        ff_error = "Yes"
    # Health Care Top Performing Stocks
    try:
        health_care_filter = tickerModel.objects.filter(sector="Healthcare")
        hcf_q2 = health_care_filter.order_by('-percentage_change')[0]
        hcf_q3 = health_care_filter.order_by('-percentage_change')[1]
        hcf_q4 = health_care_filter.order_by('-percentage_change')[2]
        hcf_set = []
        hcf_set.append(hcf_q2)
        hcf_set.append(hcf_q3)
        hcf_set.append(hcf_q4)
        print(hcf_set)
        hcf_error = "None"
    except:
        hcf_set = []
        hcf_error = "Yes"
    # Industrials Top Performing Stocks
    try:
        industrials_filter = tickerModel.objects.filter(sector="Industrials")
        if_q2 = industrials_filter.order_by('-percentage_change')[0]
        if_q3 = industrials_filter.order_by('-percentage_change')[1]
        if_q4 = industrials_filter.order_by('-percentage_change')[2]
        if_set = []
        if_set.append(if_q2)
        if_set.append(if_q3)
        if_set.append(if_q4)
        print(if_set)
        if_error = "None"
    except:
        if_set = []
        if_error = "Yes"
    # Materials Top Performing Stocks
    try:
        materials_filter = tickerModel.objects.filter(sector="Basic Materials")
        mf_q2 = materials_filter.order_by('-percentage_change')[0]
        mf_q3 = materials_filter.order_by('-percentage_change')[1]
        mf_q4 = materials_filter.order_by('-percentage_change')[2]
        mf_set = []
        mf_set.append(mf_q2)
        mf_set.append(mf_q3)
        mf_set.append(mf_q4)
        print(mf_set)
        mf_error = "None"
    except:
        mf_set = []
        mf_error = "Yes"
    # Real Estate Top Performing Stocks
    try:
        real_estate_filter = tickerModel.objects.filter(sector="Real Estate")
        ref_q2 = real_estate_filter.order_by('-percentage_change')[0]
        ref_q3 = real_estate_filter.order_by('-percentage_change')[1]
        ref_q4 = real_estate_filter.order_by('-percentage_change')[2]
        ref_set = []
        ref_set.append(ref_q2)
        ref_set.append(ref_q3)
        ref_set.append(ref_q4)
        print(ref_set)
        ref_error = "None"
    except:
        ref_set = []
        ref_error = "Yes"
    # Utilities Top Performing Stocks
    try:
        utilities_filter = tickerModel.objects.filter(sector="Utilities")
        uf_q2 = utilities_filter.order_by('-percentage_change')[0]
        uf_q3 = utilities_filter.order_by('-percentage_change')[1]
        uf_q4 = utilities_filter.order_by('-percentage_change')[2]
        uf_set = []
        uf_set.append(uf_q2)
        uf_set.append(uf_q3)
        uf_set.append(uf_q4)
        print(uf_set)
        uf_error = "None"
    except:
        uf_set = []
        uf_error = "Yes"

    context = {
        'communication_services_name': communication_services.sector_name,
        'communication_services_pctchange': communication_services.percent_change,
        'consumer_descretionary_name': consumer_descretionary.sector_name,
        'consumer_descretionary_pctchange': consumer_descretionary.percent_change,
        'consumer_staples_name': consumer_staples.sector_name,
        'consumer_staples_pctchange': consumer_staples.percent_change,
        'energy_name': energy.sector_name,
        'energy_pctchange': energy.percent_change,
        'financials_name': financials.sector_name,
        'financials_pctchange': financials.percent_change,
        'health_care_name': health_care.sector_name,
        'health_care_pctchange': health_care.percent_change,
        'industrials_name': industrials.sector_name,
        'industrials_pctchange': industrials.percent_change,
        'information_technology_name': information_technology.sector_name,
        'information_technology_pctchange': information_technology.percent_change,
        'materials_name': materials.sector_name,
        'materials_pctchange': materials.percent_change,
        'real_estate_name': real_estate.sector_name,
        'real_estate_pctchange': real_estate.percent_change,
        'utilities_name': utilities.sector_name,
        'utilities_pctchange': utilities.percent_change,
        'ccf_set': ccf_set,
        'ccf_error': ccf_error,
        'tf_set': tf_set,
        'tf_error': tf_error,
        'csf_set': csf_set,
        'csf_error': csf_error,
        'ef_set': ef_set,
        'ef_error': ef_error,
        'ff_set': ff_set,
        'ff_error': ff_error,
        'hcf_set': hcf_set,
        'hcf_error': hcf_error,
        'if_set': if_set,
        'if_error': if_error,
        'mf_set': mf_set,
        'mf_error': mf_error,
        'ref_set': ref_set,
        'ref_error': ref_error,
        'uf_set': uf_set,
        'uf_error': uf_error,
        'cstf_set': cstf_set,
        'cstf_error': cstf_error,
    }
    return render(request, 'sector_page.html', context)

@login_required(login_url='login')
def add_stock(request):
    current_user = request.user
    try:
        if request.user.is_authenticated:
            stockName = []
            sector = []
            marketcap = []
            yearhigh = []
            yearlow = []
            closingprice = []
            currentPrice = []
            previousClosingPrice = []
            priceChange = []
            decimalChange = []
            PosNegChange = []
            percentageChange = []
            recommendation = []
            package = OwnedPackage.objects.get(user=current_user).packageNum
            users_stocks = tickerModel.objects.filter(ownedBy=current_user)
            for i in range(0, len(users_stocks)):
                # Create Arrays for each stock market data set
                index = []
                open = []
                high = []
                low = []
                close = []
                stock = users_stocks[i]
                # Find database record with tickerModel entered in input field
                tickerModel_db = tickerModel.objects.get(tickerModel=stock)
                # Split long string from database by each comma and create array
                open_list = tickerModel_db.open.split(",")
                # Delete last item in array since its messed up
                del open_list[-1]
                # Make each item in array into a float number instead of string
                for n in open_list:
                    open.append(float(n))

                # Do this for the rest of the data sets
                high_list = tickerModel_db.high.split(",")
                del high_list[-1]
                for n in high_list:
                    high.append(float(n))

                low_list = tickerModel_db.low.split(",")
                del low_list[-1]
                for n in low_list:
                    low.append(float(n))

                close_list = tickerModel_db.close.split(",")
                del close_list[-1]
                for n in close_list:
                    close.append(float(n))

                index_list = tickerModel_db.index.split(",")
                del index_list[-1]
                for n in index_list:
                    t = pd.to_datetime(str(n))
                    timestring = t.strftime('%Y-%m-%d')
                    index.append(timestring)

                # outputs last in array which should be the newest
                macd_list = tickerModel_db.macd.split(",")
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
                sector.append(tickerModel_db.sector)
                marketcap.append(tickerModel_db.market_cap)
                yearhigh.append(tickerModel_db.year_high)
                yearlow.append(tickerModel_db.year_low)
                closingprice.append(close[0])
                currentPrice.append(close[0])
                previousClosingPrice.append(close[1])
                priceChange.append(round(abs(close[0] - close[1])))
                decimalChange_num = close[0] / close[1]
                decimalChange.append(decimalChange_num)
                PosNegChange_num = decimalChange_num - 1
                PosNegChange.append(PosNegChange_num)
                percentageChange_num = round(PosNegChange_num * 100, 2)
                percentageChange.append(percentageChange_num)
                recommendation.append(tickerModel_db.recommendation)
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
        context = {
            'users_stocks': users_stocks,
            'output': output,
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
            'percentageChange': percentageChange,
            'previousClosingPrice': previousClosingPrice,
            'priceChange': priceChange,
            'candlestick': candlestick(),
            'macd': round(macd, 2),
            'recommendation': recommendation,
            'package': package
        }
    except:
        message = "test"
        context = {
            'message': message,
            'package': package
        }
        print(package)
    return render(request, 'add_stock.html', context)

# @login_required(login_url='login')
# def UpdateDatabase(request):
#     # I2CGXL68P1CJ9XNP
#     # YX9741BHQFXIYA0B
#     api_key = 'AYB32JWT41PK80BR'
#     tag_list = ['GOOG', 'NOK', 'GME', 'AMC', 'DAL', 'CCL', 'AMZN', 'PLTR', 'AAPL', 'TSLA']
#
#     # sp500 names
#     sp500 = []
#     with open("capstone/sp500.csv", newline='') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             sp500.append(row[0])
#
#     print(sp500)
#
#     for f in range(209, 249):
#         time.sleep(100)
#         # Get Daily Historical Stock Data from Alphavantage API
#         ts = TimeSeries(key=api_key, output_format='pandas')
#         data_ts, meta_data_ts = ts.get_daily(symbol=sp500[f])
#
#         ts_df = data_ts
#
#         payload = {'function': 'OVERVIEW', 'symbol': sp500[f], 'apikey': 'I2CGXL68P1CJ9XNP'}
#         r = requests.get('https://www.alphavantage.co/query', params=payload)
#         r = r.json()
#
#         # Set string variables for each historical stock data set
#         openString= ""
#         closeString = ""
#         highString = ""
#         lowString = ""
#         indexString = ""
#
#         # Convert opening prices into one long string
#         for s in ts_df['1. open'].values:
#             openString += str(s) + ", "
#
#         # Convert high prices into one long string
#         for s in ts_df['2. high'].values:
#             highString += str(s) + ", "
#
#         # Convert low prices into one long string
#         for s in ts_df['3. low'].values:
#             lowString += str(s) + ", "
#
#         # Convert close prices into one long string
#         for s in ts_df['4. close'].values:
#             closeString += str(s) + ", "
#
#         # Convert date range into one long string
#         for s in ts_df.index.values:
#             indexString += str(s) + ", "
#
#         # Grab specific stock data from alphavantage api
#         stockName = r['Name']
#         sector = r['Sector']
#         marketcap = r['MarketCapitalization']
#         peratio = r['PERatio']
#         yearhigh = r['52WeekHigh']
#         yearlow = r['52WeekLow']
#         eps = r['EPS']
#
#
#
#         # Put closing prices into array for other data calculations like previous closing price etc...
#         timeseries = ts_df.to_dict(orient='records')
#         closingprice = []
#         for k in timeseries:
#             closingprice.append(k['4. close'])
#         print(ts_df)
#         def human_format(num):
#             magnitude = 0
#             while abs(num) >= 1000:
#                 magnitude += 1
#                 num /= 1000.0
#             # add more suffixes if you need them
#             return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
#
#         #-----------------------------------------------ema------------------------------------------------------------#
#         #calaculate ema
#         #save  a original ema value array, each update pull last ema calculate new one save
#         #array of closed values with last one being the current day, n = n-day ema to calculate, n<= total close values
#         def ema_initial(close, n): #outputs ema array (old->new)
#             ema = []
#             sma = sum(close[:n])
#             ema.append(sma/n)
#             for i in range(n, len(close)):
#                 weight = 2/(1 + n)
#                 ema.append((close[i] * weight) + (ema[-1] * (1 - weight)))
#             print('current days ', n, '- day ema: ', ema[-1])
#             return ema
#
#         def macd_initial(twelve, tsix):
#             macdArray = []
#             #goes in reverse to the the mismatch in lengths of 26-day emas vs 12-day emas
#             for i in range(len(tsix) - 1, -1, -1):
#                 macdArray.append(twelve[i] - tsix[i])
#
#             # reverse the list from (new...older) to (old...newer)
#             return [ele for ele in reversed(macdArray)]
#
#         # returns single value, but takes in oldemas [-1] is newest
#         def ema_new(oldEmas, close, n):
#             weight = 2 / (1 + n)
#             newEma = (close * weight) + (oldEmas[-1] * (1 - weight))
#             return newEma
#
#         #saving original closing price and reversing it so (old->new) to help with calculations
#         closingprice_ema = np.array(closingprice)[::-1]
#        # --------------------------------------------------------------------------------------------------------------#
#
#         # Data calculations
#         marketcap = int(marketcap)
#         marketcap = human_format(marketcap)
#         closingprice = closingprice[0:15]
#         currentPrice = closingprice[0]
#         previousClosingPrice = closingprice[1]
#         priceChange = closingprice[0] - closingprice[1]
#         decimalChange = closingprice[0] / closingprice[1]
#         PosNegChange = decimalChange - 1
#         percentageChange = PosNegChange * 100
#         print(f, sp500[f])
#
#         # Updating database
#         # If stock is already created in database, update that database
#         try:
#             test = tickerModel.objects.get(tickerModel=sp500[f])
#
#             #Convert needed arrays to floats
#             ema12_string_array = test.ema12.replace(' ', '').split(",")
#             ema26_string_array = test.ema26.replace(' ', '').split(",")
#             macd_signal_string_array = test.macd_signal.replace(' ', '').split(",")
#             del ema12_string_array[-1]
#             del ema26_string_array[-1]
#             del macd_signal_string_array[-1]
#
#             day12 = [float(x) for x in ema12_string_array]
#             day26 = [float(x) for x in ema26_string_array]
#             macdSignalLine = [float(x) for x in macd_signal_string_array]
#
#             #acts as if newest closing value is [-1], calculates new values for the day
#             ema12 = str(ema_new(day12, closingprice_ema[-1], 12))
#             ema26 = str(ema_new(day26, closingprice_ema[-1], 26))
#             macd_string = day12[-1] - day26[-1]
#             macd_signal_string = str(ema_new(macdSignalLine, macd_string, 9))
#             macd_string = str(macd_string)
#
#             print('Updating ', stockName, '...')
#             test.stock_name = stockName
#             test.sector = sector
#             test.market_cap = marketcap
#             test.current_price = currentPrice
#             test.previous_closing_price = previousClosingPrice
#             test.percentage_change = percentageChange
#             test.year_high = yearhigh
#             test.year_low = yearlow
#             test.price_change = priceChange
#             test.close = closeString
#             test.open = openString
#             test.high = highString
#             test.low = lowString
#             test.index = indexString
#             test.ema12 = test.ema12 + ema12 + ', '
#             test.ema26 = test.ema26 + ema26 + ', '
#             test.macd = test.macd + macd_string + ', '
#             test.macd_signal = test.macd_signal + macd_signal_string + ', '
#
#             #if macd is crossing above signal line buy else sell
#             if float(macd_string) > float(macd_signal_string):
#                 test.recommendation = 'Buy (Hold)'
#             else:
#                 test.recommendation = 'Sell'
#
#             test.save()
#             print('Updated: ', stockName)
#
#         # If stock is NOT created in database, Create that database record
#         except:
#             print("Creating ", stockName, "...")
#
#             #building initial emas should only run if stock doesnt already exist
#             day12 = ema_initial(closingprice_ema, 12)
#             day26 = ema_initial(closingprice_ema, 26)
#             macd = macd_initial(day12, day26)
#             macdSignalLine = ema_initial(macd, 9)
#
#             if macd[-1] > macdSignalLine[-1]:
#                 recommend = 'Buy (Hold)'
#             else:
#                 recommend = 'Sell'
#
#             day12_string = ""
#             day26_string = ""
#             macd_string = ""
#             macdSignalLine_string = ""
#
#             #Converting to string for database
#             for s in day12:
#                 day12_string += str(s) + ", "
#             for s in day26:
#                 day26_string += str(s) + ", "
#             for s in macd:
#                 macd_string += str(s) + ", "
#             for s in macdSignalLine:
#                 macdSignalLine_string += str(s) + ", "
#
#             test = tickerModel(tickerModel=sp500[f], stock_name=stockName, sector=sector, market_cap=marketcap,
#                           current_price=currentPrice, previous_closing_price=previousClosingPrice,
#                           percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow,
#                           price_change=priceChange, open=openString, close=closeString, high=highString,
#                           low=lowString, index=indexString, ema12=day12_string, ema26=day26_string, macd=macd_string,
#                           macd_signal=macdSignalLine_string, recommendation=recommend)
#             print("Saving ", test.stock_name, " to the Database...")
#             test.save()
#
#         # Still trying to get this to work, Having api limitation issues but this
#         # makes it run two api calls at a time (update/create a database record) every 100 seconds
#         if f % 3 == 0:
#             time.sleep(100)
#     print("Finished")
#     return render(request, 'update_database.html')


def UpdateDatabase(request):
    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    #takes in dataframe of stock data, and number of months for historic data
    #returns all sells and dates, also returns an average percent change for the each month
    def historic_return_monthly(data, n):
        date = datetime.datetime.now()
        months = []
        for i in range(n + 1):
            # keeps i 0-11
            i = i - (12 * (i // 12)) if i >= 12 else i

            temp = date.month - i
            if temp > 0:
                months.append(temp)
            elif temp == 0:
                months.append(12)
            elif temp < 0:
                months.append(temp + 12)

        initial = 0  # initial value, might not be needed
        change = []  # between buy and sell
        previous = None  # value for the day before
        initial_flag = True  # for first if to run only on first loop
        sold = True  # if it was just sold
        current = 0  # current closing value with hold period
        for i in data.index:
            if i.month in months:
                if initial_flag and data.loc[i]['Recommendation'] == 'Buy (Hold)':
                    initial = data.loc[i]['Close']
                    current = data.loc[i]['Close']
                    previous = i
                    initial_flag = False
                    sold = False
                elif sold and data.loc[i]['Recommendation'] == 'Buy (Hold)' and \
                        data.loc[previous]['Recommendation'] == 'Sell':
                    current = data.loc[i]['Close']
                    sold = False
                    previous = i
                elif not sold and data.loc[i]['Recommendation'] == 'Sell' and \
                        data.loc[previous]['Recommendation'] == 'Buy (Hold)':
                    temp = data.loc[i]['Close']
                    change.append((i, (temp - current) / current))
                    sold = True
                    previous = i

        dateChangeDF = pd.DataFrame(change, columns=['Sell Date', 'Change']) # not percentages
        dateChangeDF = dateChangeDF.set_index(dateChangeDF['Sell Date'])
        dateChangeDF.drop(['Sell Date'], axis=1, inplace=True)

        monthAverage = []
        sum, count = 0, 0
        currentDate = dateChangeDF.index[0]
        for index, value in dateChangeDF.iterrows():
            if index.month == currentDate.month:
                sum += value[0]
                count += 1
            else:
                monthAverage.append((currentDate, (sum / count) * 100))
                currentDate = index
                sum = value[0]
                count = 1
        monthAverage.append((currentDate, (sum / count) * 100))
        MonthChangeDF = pd.DataFrame(monthAverage, columns=['Month', 'Percent Change'])
        MonthChangeDF = MonthChangeDF.set_index(MonthChangeDF['Month'])
        MonthChangeDF.drop(['Month'], axis=1, inplace=True)
        ###########################################
        # right now months arent unique
        ###############################################

        #return (date, change) and (month, change)
        return dateChangeDF, MonthChangeDF

    #expects dataframe of stock info, goes back as many years as possible
    #returns array of (date, year average)
    def historic_return_yearly(data):
        date = datetime.datetime.now()
        years = []  # for checking years already added
        dates = []  # full dates for each year

        for i in data.index:
            if i.year < date.year and i.year not in years:
                years.append(i.year)
                dates.append(i)


        initial = 0  # initial value, might not be needed
        change = []  # between buy and sell for year
        previous = None  # value for the day before
        initial_flag = True  # for first if to run only on first loop
        sold = True  # if it was just sold
        current = 0  # current closing value with hold period
        current_year = data.index[0]  # current year being calculated
        year_change = [] #average percent change for year

        for i in data.index:
            if i.year != current_year.year:
                year_change.append([current_year, (sum(change) / len(change)) * 100])
                current_year = i
                change = []
            if initial_flag and data.loc[i]['Recommendation'] == 'Buy (Hold)':
                initial = data.loc[i]['Close']
                current = data.loc[i]['Close']
                previous = i
                initial_flag = False
                sold = False
            elif sold and data.loc[i]['Recommendation'] == 'Buy (Hold)' and data.loc[previous][
                'Recommendation'] == 'Sell':
                current = data.loc[i]['Close']
                sold = False
                previous = i
            elif not sold and data.loc[i]['Recommendation'] == 'Sell' and data.loc[previous][
                'Recommendation'] == 'Buy (Hold)':
                temp = data.loc[i]['Close']
                change.append((temp - current) / current)
                sold = True
                previous = i
        #uncomment if 2021 is needed
        # year_change.append([current_year, (sum(change) / len(change))])
        year_changeDF = pd.DataFrame(year_change, columns=['Year', 'Percent Change'])
        year_changeDF = year_changeDF.set_index(year_changeDF['Year'])
        year_changeDF.drop(['Year'], axis=1, inplace=True)
        return year_changeDF

    #calaculate ema
    #save  a original ema value array, each update pull last ema calculate new one save
    #array of closed values with last one being the current day, n = n-day ema to calculate, n<= total close values
    def ema_initial(close, n):  # outputs ema array (old->new)
        ema = []
        sma = sum(close[:n])
        ema.append(sma / n)
        for i in range(n, len(close)):
            weight = 2 / (1 + n)
            ema.append((close[i] * weight) + (ema[-1] * (1 - weight)))
        #print('current days ', n, '- day ema: ', ema[-1])
        return ema

    def macd_initial(twelve, tsix):
        macdArray = []
        # goes in reverse to the the mismatch in lengths of 26-day emas vs 12-day emas
        for i in range(len(tsix) - 1, -1, -1):
            macdArray.append(twelve[i] - tsix[i])

        # reverse the list from (new...older) to (old...newer)
        return [ele for ele in reversed(macdArray)]

    # returns single value, but takes in oldemas [-1] is newest
    # def ema_new(oldEmas, close, n):
    #     weight = 2 / (1 + n)
    #     newEma = (close * weight) + (oldEmas[-1] * (1 - weight))
    #     return newEma

    # --------------------------------------------------------------------------------------------------------------#
    # --------------------------------------------------------------------------------------------------------------#

    #df = pd.read_json(result, orient='index') for reading in from database
    df = pd.read_csv('capstone/sp500.csv')
    #test_symbols = ['AMZN']
    # for ticker in test_symbols:
    with alive_bar(len(df)) as bar:
        count = 0
        for index, ticker in df.iterrows():
            ticker = ticker[0]
            stock = yf.Ticker(ticker)
            stockData = stock.history(period='10y', interval='1d', progress=False)
            stockInfo = stock.info

            stockData = stockData.drop(columns=['Dividends', 'Stock Splits'])
            stockData.insert(0, 'Symbol', ticker)

            #adding empty columns
            stockData.insert(stockData.shape[1], 'EMA12', 0)
            stockData.insert(stockData.shape[1], 'EMA26', 0)
            stockData.insert(stockData.shape[1], 'MACD', 0)
            stockData.insert(stockData.shape[1], 'MACDSignal', 0)
            stockData.insert(stockData.shape[1], 'Recommendation', 'Sell')

            #calculating ema12, adjusting its size to match dataframe  and adding to dataframe
            ema12 = ema_initial(stockData['Close'], 12)
            ema12_adjusted = [ema12[0]] * 11
            ema12_adjusted.extend(ema12)
            stockData['EMA12'] = ema12_adjusted

            #calculating ema26, adjusting its size to match dataframe  and adding to dataframe
            ema26 = ema_initial(stockData['Close'], 26)
            ema26_adjusted = [ema26[0]] * 25
            ema26_adjusted.extend(ema26)
            stockData['EMA26'] = ema26_adjusted

            #calculating macd and adding to dataframe
            macd = macd_initial(ema12_adjusted, ema26_adjusted)
            stockData['MACD'] = macd

            #calculating macdSignal, adjusting its size to match dataframe and adding to dataframe
            macdSignal = ema_initial(macd, 9)
            macdSignal_adjusted = [macd[0]] * 8
            macdSignal_adjusted.extend(macdSignal)
            stockData['MACDSignal'] = macdSignal_adjusted

            #finding buy or sell and add to dataframe
            for i in stockData.index:
                if stockData.loc[i, 'MACD'] >= stockData.loc[i, 'MACDSignal']:
                    stockData.loc[i, 'Recommendation'] = 'Buy (Hold)'
                else:
                    stockData.loc[i, 'Recommendation'] = 'Sell'

            #dataframes: dateChange = sell day, change for all 12 months
            #monthlyChange = just month, average percent change for month
            dateChange, monthlyChange = historic_return_monthly(stockData, 12)


            #dataframe: (year, percent change)
            yearChange = historic_return_yearly(stockData)

            # Tries to grab specific stock data from stock.info
            # if info we want not found ignore stock
            try:
                stockName = stockInfo['longName']
                sector = stockInfo['sector']
                marketcap = stockInfo['marketCap']
                yearhigh = stockInfo['fiftyTwoWeekHigh']
                yearlow = stockInfo['fiftyTwoWeekLow']
            except:
                print(ticker, 'Info not found')
                bar()
                continue

            # Data calculations
            marketcap = human_format(marketcap)
            currentPrice = stockData['Close'][-1]
            previousClosingPrice = stockData['Close'][-2]
            priceChange = currentPrice - previousClosingPrice
            decimalChange = currentPrice / previousClosingPrice
            PosNegChange = decimalChange - 1
            percentageChange = PosNegChange * 100

            # Updating database
            # If stock is already created in database, update that database
            try:
                test = StockJSON.objects.get(ticker=ticker)
                #commment this out if an item to be updated
                # if stockData.index[-1].date() == datetime.datetime.now().date():
                #     print(ticker, 'is already up to date    ')
                #     bar()
                #     continue
                #print('Updating ', stockName, '...')
                test.stock_name = stockName
                test.sector = sector
                test.market_cap = marketcap
                test.current_price = currentPrice
                test.previous_closing_price = previousClosingPrice
                test.percentage_change = percentageChange
                test.year_high = yearhigh
                test.year_low = yearlow
                test.price_change = priceChange

                monthly = monthlyChange.to_json(orient="index")
                yearly = yearChange.to_json(orient="index")
                result = stockData.to_json(orient="index")

                test.historic_monthly = monthly
                test.historic_yearly = yearly
                test.info = result

                test.save()
               # print('Updated: ', stockName)

            # If stock is NOT created in database, Create that database record
            except:
                #print("Creating ", stockName, "...")
                result = stockData.to_json(orient="index")
                monthly = monthlyChange.to_json(orient="index")
                yearly = yearChange.to_json(orient="index")

                test = StockJSON(ticker=ticker, stock_name=stockName, sector=sector, market_cap=marketcap,
                                 current_price=currentPrice, previous_closing_price=previousClosingPrice,
                                 percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow,
                                 price_change=priceChange, info=result, historic_monthly=monthly,
                                 historic_yearly=yearly)
                #print("Saving ", test.stock_name, " to the Database...")
                test.save()
            bar()
            break
    print("Finished")
    return render(request, 'update_database.html')


@login_required(login_url='login')
def UpdateSector(request):
    sector_list = [
        "Communication Services",
        "Consumer Discretionary",
        "Consumer Staples",
        "Energy",
        "Financials",
        "Health Care",
        "Industrials",
        "Information Technology",
        "Materials",
        "Real Estate",
        "Utilities"
    ]
    # Web scrape from this url
    my_url = "https://eresearch.fidelity.com/eresearch/goto/markets_sectors/landing.jhtml"
    # Use webdriver to simulate opening webpage in order to scrape dynamic data
    driver = webdriver.Chrome('tests/chromedriver.exe')
    driver.get(my_url)
    # Find percentage change for each sector through html id's
    communication_services = driver.find_element_by_id(id_='lc50').text
    consumer_descretionary = driver.find_element_by_id(id_='lc25').text
    consumer_staples = driver.find_element_by_id(id_='lc30').text
    energy = driver.find_element_by_id(id_='lc10').text
    financials = driver.find_element_by_id(id_='lc40').text
    health_care = driver.find_element_by_id(id_='lc35').text
    industrials = driver.find_element_by_id(id_='lc20').text
    information_technology = driver.find_element_by_id(id_='lc45').text
    materials = driver.find_element_by_id(id_='lc15').text
    real_estate = driver.find_element_by_id(id_='lc60').text
    utilities = driver.find_element_by_id(id_='lc55').text

    for f in range(0, len(sector_list)):
        try:
            sector_db = Sector.objects.get(sector_name=sector_list[f])
            if (sector_list[f] == "Communication Services"):
                sector_db.percent_change = communication_services
                sector_db.save()
            if (sector_list[f] == "Consumer Discretionary"):
                sector_db.percent_change = consumer_descretionary
                sector_db.save()
            if (sector_list[f] == "Consumer Staples"):
                sector_db.percent_change = consumer_staples
                sector_db.save()
            if (sector_list[f] == "Energy"):
                sector_db.percent_change = energy
                sector_db.save()
            if (sector_list[f] == "Financials"):
                sector_db.percent_change = financials
                sector_db.save()
            if (sector_list[f] == "Health Care"):
                sector_db.percent_change = health_care
                sector_db.save()
            if (sector_list[f] == "Industrials"):
                sector_db.percent_change = industrials
                sector_db.save()
            if (sector_list[f] == "Information Technology"):
                sector_db.percent_change = information_technology
                sector_db.save()
            if (sector_list[f] == "Materials"):
                sector_db.percent_change = materials
                sector_db.save()
            if (sector_list[f] == "Real Estate"):
                sector_db.percent_change = real_estate
                sector_db.save()
            if (sector_list[f] == "Utilities"):
                sector_db.percent_change = utilities
                sector_db.save()
            print('Updated: ', sector_list[f])

        except:
            print("Failed to update database for table: Sectors")

    return render(request, 'update_sector.html')

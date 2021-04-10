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
import plotly.express as px
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
pd.options.display.max_rows = 9999

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
            print("test")
            # Make tickerModel entered to uppercase before running database check
            stock = request.POST['stock'].upper()
            print("test - ")
            stockModel = StockJSON.objects.get(ticker=stock)
            stockInfo = yf.Ticker(stock).info
            # print(stockInfo)
            print("test2")
            df = pd.read_json(stockModel.info, orient='index')
            def candlestick():
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
                figure.update_yaxes(title_text="Price ($)")
                figure.update_xaxes(title_text="Year")
                candlestick_div = plot(figure, output_type='div')
                return candlestick_div

            print("test 3")
            #if we want a company summary on stock page
            try:
                summary = stockInfo['longBusinessSummary']
            except:
                summary = 'No summary available'
            historic_monthly = json.loads(stockModel.historic_monthly)
            historic_yearly = pd.read_json(stockModel.historic_yearly, orient='index')
            historic_yearly = historic_yearly.to_dict(orient='index')
            historic_sales = json.loads(stockModel.historic_sales)
            months = []
            percentchg = []
            colors = []
            print("Recommendation Values")
            for item in reversed(historic_monthly.values()):
                print(item['Month'], " ", item['Percent_Change'])
                if item['Month'] == 1:
                    month = "Jan"
                elif item['Month'] == 2:
                    month = "Feb"
                elif item['Month'] == 3:
                    month = "Mar"
                elif item['Month'] == 4:
                    month = "Apr"
                elif item['Month'] == 5:
                    month = "May"
                elif item['Month'] == 6:
                    month = "Jun"
                elif item['Month'] == 7:
                    month = "Jul"
                elif item['Month'] == 8:
                    month = "Aug"
                elif item['Month'] == 9:
                    month = "Sep"
                elif item['Month'] == 10:
                    month = "Oct"
                elif item['Month'] == 11:
                    month = "Nov"
                elif item['Month'] == 12:
                    month = "Dec"
                if item['Percent_Change'] >= 0:
                    color = "#1ab188"
                elif item['Percent_Change'] < 0:
                    color = "#b92e34"
                months.append(month + " " + str(item['Year']))
                colors.append('#1ab188')
                percentchg.append(item['Percent_Change'])

            months2 = []
            percentchg2 = []
            colors2 = []
            print("Buy/Hold Values")
            for item in reversed(historic_monthly.values()):
                print(item['Month'], " ", round(item['Buy_Hold_Change'], 2))
                if item['Month'] == 1:
                    month2 = "Jan"
                elif item['Month'] == 2:
                    month2 = "Feb"
                elif item['Month'] == 3:
                    month2 = "Mar"
                elif item['Month'] == 4:
                    month2 = "Apr"
                elif item['Month'] == 5:
                    month2 = "May"
                elif item['Month'] == 6:
                    month2 = "Jun"
                elif item['Month'] == 7:
                    month2 = "Jul"
                elif item['Month'] == 8:
                    month2 = "Aug"
                elif item['Month'] == 9:
                    month2 = "Sep"
                elif item['Month'] == 10:
                    month2 = "Oct"
                elif item['Month'] == 11:
                    month2 = "Nov"
                elif item['Month'] == 12:
                    month2 = "Dec"
                if item['Percent_Change'] >= 0:
                    color2 = "#1ab188"
                elif item['Percent_Change'] < 0:
                    color2 = "#b92e34"
                months2.append(month2)
                colors2.append('#007bff')
                percentchg2.append(round(item['Buy_Hold_Change'], 2))


            # Create Candlestick graph from newly created dataframe
            def bar():
                figure = go.Figure(
                    [
                        go.Bar(
                            name='Recommendation',
                            x=months,
                            y=percentchg,
                            text=percentchg,
                            textposition='auto',
                            marker={'color': colors},
                        ),
                        go.Bar(
                            name='Buy/Hold',
                            x=months,
                            y=percentchg2,
                            text=percentchg2,
                            textposition='auto',
                            marker={'color': colors2},
                        )
                    ]
                )
                figure.update_layout(title_text='Recommendation System Historic Return Vs Holding Stock Return')
                figure.update_yaxes(title_text="Percent Change (%)")
                figure.update_xaxes(title_text="Month")
                bar_div = plot(figure, output_type='div')
                return bar_div
            data = json.loads(stockModel.historic_monthly)
            context = {
                'monthlyBarChart': bar(),
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
                'priceChange': stockModel.price_change,
                'candlestick': candlestick(),
                'macd': df['MACD'][-1],
                'recommendation': df['Recommendation'][-1],
                'historic_monthly': historic_monthly,
                'historic_yearly': historic_yearly,
                'historic_sales': historic_sales
            }
            return render(request, 'show_graph.html', context)
        except Exception as e:
            print(e)
            context = {
                'incorrectString': True,
            }
            return render(request, 'show_graph.html', context)
    else:
        return render(request, 'show_graph.html')


def pricing(request):
    context = {}
    current_user = request.user
    users_stocks_count = len(StockJSON.objects.filter(ownedBy=current_user))
    if request.method == 'POST':
        userPackage = OwnedPackage.objects.get(user=request.user)
        if 'starter_submit' in request.POST:
            if userPackage.packageNum != 0 and users_stocks_count <= 1:
                userPackage.packageNum = 0
                messages.success(request, 'Successfully added Starter Package to account')
                userPackage.save()
                return redirect('../')
            else:
                count = users_stocks_count - 1
                str(count)
                messages.error(request, 'Please remove %s stock(s) from your portfolio to downgrade to this package' % count)
                return redirect('../')
        elif 'deluxe_submit' in request.POST:
            if userPackage.packageNum != 1 and users_stocks_count <= 3:
                userPackage.packageNum = 1
                messages.success(request, 'Successfully added Deluxe Package to account')
                userPackage.save()
                return redirect('../')
            else:
                count = users_stocks_count - 3
                str(count)
                messages.error(request, 'Please remove %s stock(s) from your portfolio to downgrade to this package' % count)
                return redirect('../')
        elif 'ultimate_submit' in request.POST:
            if userPackage.packageNum != 2:
                userPackage.packageNum = 2
                messages.success(request, 'Successfully added Ultimate Package to account')
                userPackage.save()
                return redirect('../')

    return render(request, 'pricing.html', {'num': OwnedPackage.objects.get(user=request.user).packageNum})


def sectorPage(request):
    cyc = StockJSON.objects.filter(sector="Consumer Cyclical")
    print("Consumer Defensive", cyc)
    test = StockJSON.objects.filter(sector="Consumer Defensive")
    print("Consumer Defensive", test)
    test1 = StockJSON.objects.filter(sector="Technology")
    print("Technology", test1)
    comserv = StockJSON.objects.filter(sector="Communication Services")
    print("Communication Services", comserv)
    energy = StockJSON.objects.filter(sector="Energy")
    print("Energy", energy)
    financ = StockJSON.objects.filter(sector="Financial Services")
    print("Financial Services", financ)
    health = StockJSON.objects.filter(sector="Healthcare")
    print("Healthcare", health)
    indust = StockJSON.objects.filter(sector="Industrials")
    print("Industrials", indust)
    material = StockJSON.objects.filter(sector="Basic Materials")
    print("Basic Materials", material)
    estate = StockJSON.objects.filter(sector="Real Estate")
    print("Real Estate", estate)
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
        consumer_cyclical_filter = StockJSON.objects.filter(sector="Consumer Cyclical")
        ccf_q2 = consumer_cyclical_filter.order_by('-percentage_change')[0]
        ccf_q3 = consumer_cyclical_filter.order_by('-percentage_change')[1]
        ccf_q4 = consumer_cyclical_filter.order_by('-percentage_change')[2]
        ccf_set = []
        ccf_set.append(ccf_q2)
        ccf_set.append(ccf_q3)
        ccf_set.append(ccf_q4)
        ccf_error = "None"
    except:
        ccf_set = []
        ccf_error = "Yes"
    # Consumer Staples Top Performing Stocks
    try:
        consumer_staples_filter = StockJSON.objects.filter(sector="Consumer Defensive")
        cstf_q2 = consumer_staples_filter.order_by('-percentage_change')[0]
        cstf_q3 = consumer_staples_filter.order_by('-percentage_change')[1]
        cstf_q4 = consumer_staples_filter.order_by('-percentage_change')[2]
        cstf_set = []
        cstf_set.append(cstf_q2)
        cstf_set.append(cstf_q3)
        cstf_set.append(cstf_q4)
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
        tf_error = "None"
    except:
        tf_set = []
        tf_error = "Yes"
    # Communication Services Top Performing Stocks
    try:
        communication_services_filter = StockJSON.objects.filter(sector="Communication Services")
        csf_q2 = communication_services_filter.order_by('-percentage_change')[0]
        csf_q3 = communication_services_filter.order_by('-percentage_change')[1]
        csf_q4 = communication_services_filter.order_by('-percentage_change')[2]
        csf_set = []
        csf_set.append(csf_q2)
        csf_set.append(csf_q3)
        csf_set.append(csf_q4)
        csf_error = "None"
    except:
        csf_set = []
        csf_error = "Yes"
    # Energy Top Performing Stocks
    try:
        energy_filter = StockJSON.objects.filter(sector="Energy")
        ef_q2 = energy_filter.order_by('-percentage_change')[0]
        ef_q3 = energy_filter.order_by('-percentage_change')[1]
        ef_q4 = energy_filter.order_by('-percentage_change')[2]
        ef_set = []
        ef_set.append(ef_q2)
        ef_set.append(ef_q3)
        ef_set.append(ef_q4)
        ef_error = "None"
    except:
        ef_set = []
        ef_error = "Yes"
    # Financials Top Performing Stocks
    try:
        financials_filter = StockJSON.objects.filter(sector="Financial Services")
        ff_q2 = financials_filter.order_by('-percentage_change')[0]
        ff_q3 = financials_filter.order_by('-percentage_change')[1]
        ff_q4 = financials_filter.order_by('-percentage_change')[2]
        ff_set = []
        ff_set.append(ff_q2)
        ff_set.append(ff_q3)
        ff_set.append(ff_q4)
        ff_error = "None"
    except:
        ff_set = []
        ff_error = "Yes"
    # Health Care Top Performing Stocks
    try:
        health_care_filter = StockJSON.objects.filter(sector="Healthcare")
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
        industrials_filter = StockJSON.objects.filter(sector="Industrials")
        if_q2 = industrials_filter.order_by('-percentage_change')[0]
        if_q3 = industrials_filter.order_by('-percentage_change')[1]
        if_q4 = industrials_filter.order_by('-percentage_change')[2]
        if_set = []
        if_set.append(if_q2)
        if_set.append(if_q3)
        if_set.append(if_q4)
        if_error = "None"
    except:
        if_set = []
        if_error = "Yes"
    # Materials Top Performing Stocks
    try:
        materials_filter = StockJSON.objects.filter(sector="Basic Materials")
        mf_q2 = materials_filter.order_by('-percentage_change')[0]
        mf_q3 = materials_filter.order_by('-percentage_change')[1]
        mf_q4 = materials_filter.order_by('-percentage_change')[2]
        mf_set = []
        mf_set.append(mf_q2)
        mf_set.append(mf_q3)
        mf_set.append(mf_q4)
        mf_error = "None"
    except:
        mf_set = []
        mf_error = "Yes"
    # Real Estate Top Performing Stocks
    try:
        real_estate_filter = StockJSON.objects.filter(sector="Real Estate")
        ref_q2 = real_estate_filter.order_by('-percentage_change')[0]
        ref_q3 = real_estate_filter.order_by('-percentage_change')[1]
        ref_q4 = real_estate_filter.order_by('-percentage_change')[2]
        ref_set = []
        ref_set.append(ref_q2)
        ref_set.append(ref_q3)
        ref_set.append(ref_q4)
        ref_error = "None"
    except:
        ref_set = []
        ref_error = "Yes"
    # Utilities Top Performing Stocks
    try:
        utilities_filter = StockJSON.objects.filter(sector="Utilities")
        uf_q2 = utilities_filter.order_by('-percentage_change')[0]
        uf_q3 = utilities_filter.order_by('-percentage_change')[1]
        uf_q4 = utilities_filter.order_by('-percentage_change')[2]
        uf_set = []
        uf_set.append(uf_q2)
        uf_set.append(uf_q3)
        uf_set.append(uf_q4)
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
            percentageChange = []
            recommendation = []
            output=[]
            package = OwnedPackage.objects.get(user=current_user).packageNum
            users_stocks = StockJSON.objects.filter(ownedBy=current_user)
            #print(users_stocks)
            for i in range(0, len(users_stocks)):
                stock = users_stocks[i]
                #print("stock", stock)

                # Find database record with tickerModel entered in input field
                tickerModel_db = StockJSON.objects.get(ticker=stock)
                #print(marketcap)

                # Run Data Calculations
                sector.append(tickerModel_db.sector)
                marketcap.append(tickerModel_db.market_cap)
                yearhigh.append(tickerModel_db.year_high)
                yearlow.append(tickerModel_db.year_low)
                currentPrice.append(tickerModel_db.current_price)
                previousClosingPrice.append(tickerModel_db.previous_closing_price)
                priceChange.append(tickerModel_db.price_change)
                percentageChange.append(tickerModel_db.percentage_change)

                df = pd.read_json(tickerModel_db.info, orient='index')
                #print(df['Recommendation'][-1])
                recommendation.append(df['Recommendation'][-1])
                # test = tickerModel_db.info
                # stockModel = StockJSON.objects.get(ticker = stock)
                # stockInfo = yf.Ticker(stock).info
                # print(stockInfo)
                # print(test['Recommendation'][-1])

            packageLookup = {0: 1, 1: 3, 2: 5}
            if request.method == 'POST':
                if len(users_stocks) < packageLookup[package]:
                    form = StockForm(request.POST or None)
                    inputtedStock = request.POST.get("ticker").upper()
                    updateStock = StockJSON.objects.get(ticker=inputtedStock)
                    if current_user not in updateStock.ownedBy.all():
                        updateStock.ownedBy.add(request.user)
                        if form.is_valid():
                            form.save()
                            messages.success(request, "Stock has been Added!")
                            return redirect('add_stock')
                    else:
                        messages.error(request, "Stock already in portfolio")
                        return redirect('add_stock')
                else:
                    messages.error(request, "Stock tracking limit reached: upgrade package, or delete a stock")
                    return redirect('add_stock')
            else:
                output = []
                stock = users_stocks
                output.append(stock)
        else:
            return redirect('pricing.html')

        temp = {i: {'stock': users_stocks[i], 'recommendation': recommendation[i]} for i in range(len(users_stocks))}

        context = {
            'range': np.arange(len(users_stocks)),
            'users_stocks': temp,
            'output': output,
            'currentPrice': currentPrice,
            'marketcap': marketcap,
            'yearhigh': yearhigh,
            'yearlow': yearlow,
            'closingprice': closingprice,
            'stock': stock,
            'stockName': stockName,
            'percentageChange': percentageChange,
            'previousClosingPrice': previousClosingPrice,
            'priceChange': priceChange,
            'recommendation': recommendation,
        }
    except:
        print("error")
        message = "test"
        context = {
            'message': message,
            'package': package
        }
    print(package)
    return render(request, 'add_stock.html', context)
def delete_stock(request):
    stockObj = request.GET.get("deleteButton")
    deleter = StockJSON.objects.get(ticker=stockObj)
    deleter.ownedBy.remove(request.user)
    return redirect('../')

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
        current_date = datetime.datetime.now()

        # Builds month list
        months = []
        tempYear = current_date.year
        for i in range(n, -1, -1):
            # keeps i 0-12
            i = i - (12 * (i // 12)) if i > 12 else i
            temp = current_date.month - i
            if temp > 0:
                months.append([tempYear, temp])
            elif temp == 0:
                months.append([tempYear - 1, 12])
            elif temp < 0:
                months.append([tempYear - 1, temp + 12])

        previous = None  # value for the day before
        initial_flag = True  # for first if to run only on first loop
        sold = True  # if it was just sold
        buyPrice = 0  # current closing value with hold period
        df = pd.DataFrame(columns=['Buy_Date', 'Buy_Price', 'Sell_Date', 'Sell_Price', 'Percent_Change'])
        rowDict = {'Buy_Date': 0, 'Buy_Price': 0, 'Sell_Date': 0, 'Sell_Price': 0, 'Percent_Change': 0}

        hold_change = []
        initial_month = True
        current_month = months[0][1]
        prev_month = months[0][1]
        for i, day in enumerate(data.index):
            if [day.year, day.month] in months:
                #converting string dates into ints
                day_str = '0' + str(day.day) if day.day < 10 else str(day.day)
                month_str = '0' + str(day.month) if day.month < 10 else str(day.month)
                year_str = str(day.year)

                if initial_month:
                    current_month = day
                    prev_month = day
                    initial_month = False
                if day.month != current_month.month:
                    hold_change.append([current_month.month, (data.loc[prev_month]['Close'] - data.loc[current_month]['Close'])/data.loc[current_month]['Close']])
                    current_month = day
                prev_month = day

                # first buy
                if initial_flag and data.loc[day]['Recommendation'] == 'Buy (Hold)':
                    buyPrice = data.loc[day]['Close']
                    rowDict['Buy_Date'] = month_str + '/' + day_str + '/' + year_str
                    rowDict['Buy_Price'] = round(buyPrice, 2)
                    previous = day
                    initial_flag = False
                    sold = False

                # if there was a buy just after a sell
                elif sold and data.loc[day]['Recommendation'] == 'Buy (Hold)' and \
                        data.loc[previous]['Recommendation'] == 'Sell':
                    buyPrice = data.loc[day]['Close']
                    rowDict['Buy_Date'] = month_str + '/' + day_str + '/' + year_str
                    rowDict['Buy_Price'] = round(buyPrice, 2)
                    sold = False
                    previous = day

                # if there was sell just after a buy
                elif not sold and data.loc[day]['Recommendation'] == 'Sell' and \
                        data.loc[previous]['Recommendation'] == 'Buy (Hold)':
                    sellPrice = data.loc[day]['Close']
                    rowDict['Sell_Date'] = month_str + '/' + day_str + '/' + year_str
                    rowDict['Sell_Price'] = round(sellPrice, 2)
                    rowDict['Percent_Change'] = round(((sellPrice - buyPrice) / buyPrice) * 100, 2)
                    df = df.append(rowDict, ignore_index=True)
                    rowDict = {'Buy_Date': 0, 'Buy_Price': 0, 'Sell_Date': 0, 'Sell_Price': 0, 'Percent_Change': 0}
                    sold = True
                    previous = day

        #adds last month in
        hold_change.append([current_month.month, (data.loc[prev_month]['Close'] - data.loc[current_month]['Close']) /
                            data.loc[current_month]['Close']])
        df.insert(len(df.columns), 'Monthly_Percent_Change', 0.0)

        # appends the progressive total monthly percent change, resetting at the first sell of each month.
        monthSum = []
        totalChange = 0
        count = 0
        monthCheck = int(df['Sell_Date'][0].split('/')[0])
        yearCheck = int(df['Sell_Date'][0].split('/')[2])
        for i, value in df.iterrows():
            tempYear = int(value['Sell_Date'].split('/')[2])
            tempMonth = int(value['Sell_Date'].split('/')[0])
            if tempMonth == monthCheck and tempYear == yearCheck:
                totalChange += value['Percent_Change']
                count += 1
                df.loc[i, 'Monthly_Percent_Change'] = round(totalChange, 2)
            else:
                monthSum.append([yearCheck, monthCheck, count, round(totalChange, 2)])
                totalChange = value['Percent_Change']
                count = 1
                df.loc[i, 'Monthly_Percent_Change'] = round(totalChange, 2)
                monthCheck = int(value['Sell_Date'].split('/')[0])
                yearCheck = int(value['Sell_Date'].split('/')[2])
        monthSum.append([yearCheck, monthCheck, count, round(totalChange, 2)])
        monthSumDF = pd.DataFrame(monthSum, columns=['Year', 'Month', 'Total_Sales', 'Percent_Change'])

        #fills in months that have 0 sales
        monthSumDF2 = []
        tempI = 0
        for i, value in enumerate(months):
            if [monthSumDF.loc[tempI, 'Year'], monthSumDF.loc[tempI, 'Month']] != value:
                monthSumDF2.append([value[0], value[1], 0, 0])
            elif [monthSumDF.loc[tempI, 'Year'], monthSumDF.loc[tempI, 'Month']] == value:
                monthSumDF2.append([monthSumDF.loc[tempI, 'Year'], monthSumDF.loc[tempI, 'Month'],
                                    monthSumDF.loc[tempI, 'Total_Sales'], monthSumDF.loc[tempI, 'Percent_Change']])
                if len(monthSumDF) - 1 != tempI:
                    tempI += 1

        #monthSumDF2 = beforeList + monthSumDF2 + afterList
        hold_change = np.array(hold_change)
        monthSumDFAllMonths = pd.DataFrame(monthSumDF2, columns=['Year', 'Month', 'Total_Sales', 'Percent_Change'])
        monthSumDFAllMonths.insert(len(monthSumDFAllMonths.columns), 'Buy_Hold_Change', hold_change[:, 1:] * 100)

        # df =  buy date, buy price, sell date, sell price, percent change for each sell
        # monthSumDF = dataframe of (year, month, total sales total month change)
        return df, monthSumDFAllMonths

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

        year_hold_change = []
        end_date = data.index[0]

        for i in data.index:
            if i.year != current_year.year:
                year_change.append([current_year, round(sum(change) * 100, 2)])

                #current year is first day of the year, end_date is last day of the year
                year_hold_change.append([current_year, (data.loc[end_date]['Close'] - data.loc[current_year]['Close']) /
                                    data.loc[current_year]['Close']])
                current_year = i
                change = []
            end_date = i

            if initial_flag and data.loc[i]['Recommendation'] == 'Buy (Hold)':
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
        year_hold_change = np.array(year_hold_change)
        year_changeDF = pd.DataFrame(year_change, columns=['Year', 'Percent_Change'])
        year_changeDF = year_changeDF.set_index(year_changeDF['Year'])
        year_changeDF.drop(['Year'], axis=1, inplace=True)
        year_changeDF.insert(len(year_changeDF.columns), 'Buy_Hold_Change', year_hold_change[:, 1:] * 100)
        return year_changeDF

    #calculate ema from closing price values
    def ema_initial(close, n):  # outputs ema array (old->new)
        ema = []
        sma = sum(close[:n])
        ema.append(sma / n)
        for i in range(n, len(close)):
            weight = 2 / (1 + n)
            ema.append((close[i] * weight) + (ema[-1] * (1 - weight)))
        #print('current days ', n, '- day ema: ', ema[-1])
        return ema

    #calculate macd from ema12 and ema26
    def macd_initial(twelve, tsix):
        macdArray = []
        # goes in reverse to the the mismatch in lengths of 26-day emas vs 12-day emas
        for i in range(len(tsix) - 1, -1, -1):
            macdArray.append(twelve[i] - tsix[i])

        # reverse the list from (new...older) to (old...newer)
        return [ele for ele in reversed(macdArray)]

    # --------------------------------------------------------------------------------------------------------------#
    # --------------------------------------------------------------------------------------------------------------#

    df = pd.read_csv('capstone/sp500.csv')

    with alive_bar(len(df)) as bar:
        for index, ticker in df.iterrows():
            #print(ticker)
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

            #some stocks have bad data with NaN
            stockData = stockData.dropna(axis=0)

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
            #monthlyChange = just month, total sells, average percent change for month
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
                sales = dateChange.to_json(orient="index")
                yearly = yearChange.to_json(orient="index")
                result = stockData.to_json(orient="index")

                test.historic_monthly = monthly
                test.historic_sales = sales
                test.historic_yearly = yearly
                test.info = result

                test.save()
                #print('Updated: ', stockName)

            # If stock is NOT created in database, Create that database record
            except:
                #print("Creating ", stockName, "...")
                result = stockData.to_json(orient="index")
                monthly = monthlyChange.to_json(orient="index")
                sales = dateChange.to_json(orient="index")
                yearly = yearChange.to_json(orient="index")

                test = StockJSON(ticker=ticker, stock_name=stockName, sector=sector, market_cap=marketcap,
                                 current_price=currentPrice, previous_closing_price=previousClosingPrice,
                                 percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow,
                                 price_change=priceChange, info=result, historic_monthly=monthly,
                                 historic_yearly=yearly, historic_sales=sales)
                #print("Saving ", test.stock_name, " to the Database...")
                test.save()
            bar()
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
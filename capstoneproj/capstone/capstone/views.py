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
from .forms import StockForm
from .fusioncharts import FusionCharts
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries

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
    import requests
    import json
    if request.method == 'POST':
        ticker = request.POST['ticker']
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + ticker + "/quote?token=pk_31a9e3d6616e4a5abbfd6c82edabc089")
        try:
            api = json.loads(api_request.content)
        except Exception as e:
            api = "Error..."
        return render(request, 'dashboard.html', {'api': api})
    else:
        return render(request, 'dashboard.html', {'ticker': "Enter a Ticker Symbol Above..."})

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

@login_required(login_url='login')
def add_stock(request):
    import requests
    import json
    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, "Stock has been Added!")
            return redirect('add_stock')
    else:

        ticker = Stock.objects.all()
        output = []
        for ticker_item in ticker:
            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_31a9e3d6616e4a5abbfd6c82edabc089")
            try:
                api = json.loads(api_request.content)
                output.append(api)
            except Exception as e:
                api = "Error..."

        return render(request, 'add_stock.html', {'ticker': ticker, 'output': output})

@login_required(login_url='login')
def delete(request, stock_id):

	item = Stock.objects.get(pk=stock_id)
	item.delete()
	messages.success(request, ("Stock Has Been Deleted!"))
	return redirect(add_stock)


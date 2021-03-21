"""capstone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import VerificationView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', views.register, name='signup'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('updateinfo/', views.updateinfo, name='updateinfo'),
    path('show_graph/', views.show_stock_graph, name="show_graph"),
    path('pricing/', views.pricing, name='pricing'),
    #added
    path('sector_page/', views.sectorPage, name='sector_page'),
    #added
    path('update_database/', views.UpdateDatabase, name='update_database'),
    path('update_sector/', views.UpdateSector, name='update_sector'),
    path('add_stock.html', views.add_stock, name="add_stock"),
    #path('delete/<stock_id>', views.delete, name="delete"),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='templates/password_reset/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='templates/password_reset/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='templates/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='templates/password_reset/password_reset_complete.html'), name='password_reset_complete'),

    path('', views.add_stock, name='dashboard'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate")
]

urlpatterns += staticfiles_urlpatterns()
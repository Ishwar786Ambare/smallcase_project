# stocks/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('populate-stocks/', views.populate_stocks, name='populate_stocks'),
    path('update-prices/', views.update_prices, name='update_prices'),
    path('basket/create/', views.basket_create, name='basket_create'),
    path('basket/<int:basket_id>/', views.basket_detail, name='basket_detail'),
    path('basket/<int:basket_id>/delete/', views.basket_delete, name='basket_delete'),
    path('basket/preview/', views.preview_basket, name='preview_basket'),
]


# ======================================
# smallcase_project/urls.py
# ======================================

"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stocks.urls')),
]
"""
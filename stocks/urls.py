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
    path('basket/<int:basket_id>/edit-investment/', views.basket_edit_investment, name='basket_edit_investment'),
    path('basket/preview/', views.preview_basket, name='preview_basket'),
    path('basket-item/<int:item_id>/edit/', views.basket_item_edit, name='basket_item_edit'),
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
# stocks/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Home and stock management
    path('', views.home, name='home'),
    path('populate-stocks/', views.populate_stocks, name='populate_stocks'),
    path('update-prices/', views.update_prices, name='update_prices'),
    
    # Basket management
    path('basket/create/', views.basket_create, name='basket_create'),
    path('basket/<int:basket_id>/', views.basket_detail, name='basket_detail'),
    path('basket/<int:basket_id>/performance/', views.basket_performance, name='basket_performance'),
    path('basket/<int:basket_id>/chart-data/', views.basket_chart_data, name='basket_chart_data'),
    path('basket/<int:basket_id>/delete/', views.basket_delete, name='basket_delete'),
    path('basket/<int:basket_id>/duplicate/', views.basket_duplicate, name='basket_duplicate'),
    path('basket/<int:basket_id>/edit-investment/', views.basket_edit_investment, name='basket_edit_investment'),
    path('basket/preview/', views.preview_basket, name='preview_basket'),
    path('basket-item/<int:item_id>/edit/', views.basket_item_edit, name='basket_item_edit'),
    
    # Static pages
    path('contact/', views.contact_us, name='contact_us'),
    
    # Chat API endpoints
    path('api/chat/send/', views.chat_send_message, name='chat_send_message'),
    path('api/chat/messages/', views.chat_get_messages, name='chat_get_messages'),
    path('api/chat/groups/', views.chat_get_groups, name='chat_get_groups'),
    path('api/chat/groups/create/', views.chat_create_group, name='chat_create_group'),
    path('api/chat/groups/members/', views.chat_get_members, name='chat_get_members'),
    path('api/chat/groups/add-member/', views.chat_add_member, name='chat_add_member'),
    path('api/chat/groups/leave/', views.chat_leave_group, name='chat_leave_group'),
    path('api/chat/users/search/', views.chat_search_users, name='chat_search_users'),
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
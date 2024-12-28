from django.contrib import admin
from django.urls import include, path
from . import views
from django.urls import path

urlpatterns = [
 #   path("polls/", include("polls.urls")),
#    path("admin/", admin.site.urls),
    path('add-user/', views.UserCreateView.as_view(), name='add-user'),
    path('add-charger/', views.ChargerCreateView.as_view(), name='add-charger'),
    path('add-charging-session/', views.ChargingSessionCreateView.as_view(), name='add-charging-session'),

    path('simple/', views.simple_endpoint),
    path('transactions/', views.get_transactions),
]
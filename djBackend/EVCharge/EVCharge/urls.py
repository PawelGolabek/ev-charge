from django.contrib import admin
from django.urls import include, path
from . import views
from django.urls import path
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView


urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
 #   path("polls/", include("polls.urls")),
#    path("admin/", admin.site.urls),
    path('add-user/', views.UserCreateView.as_view(), name='add-user'),
    path('add-charger/', views.ChargerCreateView.as_view(), name='add-charger'),
    path('api/add-charging-session/', views.ChargingSessionCreateView.as_view(), name='add-charging-session'),
    path('api/check-balance/', views.CheckMyBalanceView.as_view(), name = 'check-balance'),
    path('api/increase-balance/', views.IncreaseBalanceView.as_view(),name = 'increase-balance'),
    #admin
    path('api/generate-summaries/', views.GenerateTransactionSummaryView.as_view(),name = 'summaries-generate'),
    path('api/generate-summaries-date/', views.GetDateRangeView.as_view(),name = 'summaries-generate-date'),
    path("api/fetch-summaries/", views.RetrieveTransactionSummaryView.as_view(), name = 'fetch-summaries'),
    path("api/pay-seller/", views.paySellerView.as_view(), name = 'pay-seller'),
    path("api/add-user/", views.AddUserView.as_view(), name = 'add-user'),
    #seller
    path("api/check-contribution/", views.CheckContributionView.as_view(), name = 'check-contribution'),
    path("api/add-charger/", views.AddChargerView.as_view(), name = 'add-charger'),
    path("api/update-charger/", views.UpdateChargerPriceView.as_view(), name = 'update-charger'),
    path("api/list-chargers/", views.ListMyChargersView.as_view(), name = 'list-chargers'),
    

    path('simple/', views.simple_endpoint),
    path('api/transactions/', views.GetTransactionsView.as_view(), name='transactions')

]
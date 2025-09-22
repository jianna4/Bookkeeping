# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.analyze_view, name="analyze"),
    path("price/", views.price_view, name="price"),
    path("revenue/", views.revenue_view, name="revenue"),
    path("plot/trend/", views.plot_trend_view, name="plot_trend"),
    path("plot/forecast/", views.plot_forecast_view, name="plot_forecast"),
]

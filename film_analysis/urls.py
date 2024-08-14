"""
URL configuration for film_analysis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from charts import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.chart_page,name='chart_page'),
    # path('charts/',views.generate_charts,name='generate_charts'),
    path('chart/genre/', views.chart_genre_distribution, name='chart_genre_distribution'),
    path('chart/language/', views.chart_language_distribution, name='chart_language_distribution'),
    path('chart/runtime/', views.chart_runtime_distribution, name='chart_runtime_distribution'),
    path('chart/runtime_bins/', views.chart_runtime_bins, name='chart_runtime_bins'),
    path('chart/rating/', views.chart_rating_distribution, name='chart_rating_distribution'),
    path('chart/seasonal/', views.chart_seasonal_performance, name='chart_seasonal_performance'),
    path('chart/monthly/', views.chart_monthly_trend, name='chart_monthly_trend'),

]

from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('',views.stockPicker,name='stockpicker'),
    path('stocktracker/',views.stockTracker,name='stocktracker'),

]

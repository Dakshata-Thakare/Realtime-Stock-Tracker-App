from django.contrib import admin
from django.urls import include, path

# from stockproject import mainapp
# stockproject\mainapp
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('mainapp.urls')),
]

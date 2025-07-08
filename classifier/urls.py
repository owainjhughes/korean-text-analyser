from django.urls import path, include
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path('admin/', admin.site.urls),
    #path('', include('classifier.urls')),
    path("register/", views.register, name="register"),
]

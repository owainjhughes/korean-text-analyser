from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('classifier.urls')),
    path("login/", auth_views.LoginView.as_view(), name="login"),
<<<<<<< HEAD
    path("logout/", auth_views.LogoutView.as_view(), name="logout")
=======
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
>>>>>>> 225454725c60328a89aae8f7f61e4c0200fd66d3
]

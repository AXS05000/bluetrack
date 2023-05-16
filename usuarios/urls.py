from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('usuario/', include('django.contrib.auth.urls')),
    path('login/', views.CustomLoginView, name='login'),
]

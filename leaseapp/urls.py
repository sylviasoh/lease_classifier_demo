from django.urls import include, path

from . import views

app_name = 'leaseapp'
urlpatterns = [
    path('', views.MainView, name='main'),
    path('runapp/', views.RunApp, name='runapp'),
    path('results/', views.ResultsView, name='results')
]
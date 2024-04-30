from django.urls import path
#from .views import HomePageView
from . import views

app_name = 'bash'

urlpatterns = [
    path('', views.bash_view, name='index'),
    path('phenopackets', views.phenopackets_view, name='phenopackets'),
    path('task_status/', views.task_status, name='task_status'),
    path('wt/', views.web, name='wt'),
    path('wtc/', views.async_web, name='wtc'),
    path('validator/', views.channel, name='validator')
]
from django.urls import path
#from .views import HomePageView
from . import views

app_name = 'bash'

urlpatterns = [
    path('', views.LandingPage.as_view(), name='index'),
    path('task_status/', views.task_status, name='task_status'),
    path('validator/', views.ChannelView.as_view(), name='validator')
]
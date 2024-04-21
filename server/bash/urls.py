from django.urls import path
#from .views import HomePageView
from . import views
app_name = 'bash'

urlpatterns = [
    path('', views.bash_view, name='index'),
    path('phenopackets', views.phenopackets_view, name='phenopackets')
]
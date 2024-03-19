from django.urls import path, include
from .views import home

from .views import homePage

from .views import search_and_save
from .views import get_yayin_detay


urlpatterns = [
    path('', home, name='home'),
    path('homePage/', homePage, name='homePage'),
    path('get_yayin_detay/<str:yayin_adi>/', get_yayin_detay, name='get_yayin_detay'),
    path('search_and_save/', search_and_save, name='search_and_save'),
       
]

from django.urls import path
from . import views 

urlpatterns = [
    path('home/', views.home, name="static_home"),
    path('about/',views.about, name="static_about")
]
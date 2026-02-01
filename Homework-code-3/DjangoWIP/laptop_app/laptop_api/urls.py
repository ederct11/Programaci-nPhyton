from django.urls import path
from . import views 

urlpatterns = [
    path('laptops/',views.get_laptops, name="get_laptops"),
    path('laptop/', views.post_laptop, name="post_laptop"),
    path('laptop/<str:id>/',views.handle_one_laptop, name= "handle_one_laptop"),
    path('v2/laptop/<str:id>/', views.v2, name="v2_example"),
]

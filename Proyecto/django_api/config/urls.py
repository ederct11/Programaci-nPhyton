from django.urls import path, include

urlpatterns = [
    path('api/', include('image_api.urls')),
]
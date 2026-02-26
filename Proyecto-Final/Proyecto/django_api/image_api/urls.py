from django.urls import path
from . import views

urlpatterns = [
    path('process/',        views.process_image,  name='process'),
    path('task/<task_id>/', views.task_status,     name='task_status'),
    path('workers/',        views.workers_status,  name='workers'),
    path('health/',         views.health_check,    name='health'),
    path('debug/',          views.debug_redis,     name='debug'),
]
from django.urls import path
from . import views 
from django.views.generic import RedirectView

urlpatterns = [
    path('base/',RedirectView.as_view(url='/dynamic-pages/base/Ederct'), name="base_template"),
    path('base/<str:name>',views.template_base, name="base_template_name"),
    path('materials/', views.template_materials, name="template_materials") 
]

from django.shortcuts import render
from . import models

# Create your views here.

def template_base(request, name):
    page_title = "APP Django"
    show_image = request.GET.get("show_image", True) == "True"
    print(show_image)
    context = {
        'titulo_pagina' : page_title,
        'mi_nombre': name,
        'show_img': show_image
    }
    return render(request,'base.html',context)

def template_materials(request):
    context = {
        'laptops': models.MATERIALS
    }
    return render(request,'materials.html',context)

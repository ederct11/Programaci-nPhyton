from django.db import models

# Create your models here.

class Material:
    # **kwargs Materials(name= , descrition= ..... )
    def __init__(self,dic):
        self.name= dic["name"]
        self.description= dic["description"]
        self.price_starting= dic["price_starting"]
        self.laptop_types= dic["laptop_types"]
        
        
def create_materials(dic):
    return list(map( lambda e: Material(e), dic) )

MATERIALS = create_materials([
    {
        "name": "Maletín Premium", 
        "description": "Maletín acolchado resistente al agua",
        "price_starting": 150000, 
        "laptop_types": "Asus, Lenovo, Janus"
    },
    {
        "name": "Mouse Inalámbrico",
        "description": "Mouse ergonómico con receptor USB", 
        "price_starting": 80000, 
        "laptop_types": "Acer, HP, Lenovo"
    },
    {
        "name": "Base Refrigerante",
        "description": "Con 4 ventiladores y luces LED RGB", 
        "price_starting": 120000, 
        "laptop_types": "HP, Acer, Asus"
    },
    {
        "name": "Teclado Mecánico",
        "description": "Retroiluminado con switches mecánicos", 
        "price_starting": 250000, 
        "laptop_types": "HP, Acer, Lenovo"
    }
])


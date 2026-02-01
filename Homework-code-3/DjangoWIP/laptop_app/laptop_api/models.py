from django.db import models
from datetime import datetime
from mongoengine import Document, StringField, IntField,DateTimeField
# Create your models here.

class laptopItem(Document):
    name = StringField(max_length=200, required= True)
    RAM = IntField(min_value=1, required= True)
    SSD = IntField(min_value=1, required= True)
    Price = IntField(min_value=1, required= True)
    material = StringField(max_length=20)
    creation_date = DateTimeField(default=datetime.now)
    author = StringField(max_length=20)
    
    meta = {
        'collection': "laptops",
        'ordering': ['-creation_date']
    }
    
    def as_dic(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "RAM": self.RAM,
            "SSD": self.SSD,
            "Price": self.Price,
            "material": self.material
        }        
    
    def __str__(self):
        return f"{self.name} : {self.RAM}x{self.SSD}x{self.Price} {self.material}"
    

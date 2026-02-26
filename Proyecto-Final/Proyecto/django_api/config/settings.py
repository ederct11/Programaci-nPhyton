import os

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-key-cambiar-en-produccion')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'image_api',
]

# Sin base de datos, todo vive en Redis
DATABASES = {}

ROOT_URLCONF = 'config.urls'
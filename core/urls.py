"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
import os

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'calendario', 'static', 'js', 'sw.js')
    with open(sw_path, 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

def favicon(request):
    ico_path = os.path.join(settings.BASE_DIR, 'calendario', 'static', 'favicon.ico')
    with open(ico_path, 'rb') as f:
        return HttpResponse(f.read(), content_type='image/x-icon')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker, name='service_worker'),
    path('favicon.ico', favicon, name='favicon'),
    path('', include('calendario.urls')),
]

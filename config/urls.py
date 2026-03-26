from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # On utilise uniquement le include ici
    path('', include('authentification.urls')), 
]
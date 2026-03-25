from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # On dit à Django d'utiliser les routes définies dans ton application
    path('', include('authentification.urls')), 
]
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Utilise juste le nom du fichier, Django le trouvera dans 'templates/'
    path('authentification/', TemplateView.as_view(template_name='authentification.html'), name='login'),
    path('inscription/', TemplateView.as_view(template_name='inscription.html'), name='register'),
]
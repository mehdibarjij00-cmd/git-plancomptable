from django.contrib import admin
from .models import Entreprise, CompteComptable, EcritureComptable

admin.site.register(Entreprise)
admin.site.register(CompteComptable)
admin.site.register(EcritureComptable)
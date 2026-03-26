from django.contrib import admin
from .models import Entreprise, CompteComptable, EcritureComptable, Transaction

# On enregistre tous les modèles pour pouvoir les modifier dans /admin/
admin.site.register(Entreprise)
admin.site.register(CompteComptable)
admin.site.register(EcritureComptable)
admin.site.register(Transaction) # <--- Ajoute cette ligne pour voir tes transactions
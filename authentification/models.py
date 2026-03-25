from django.db import models
from django.contrib.auth.models import User

# --- TABLE DES PME (Clients du cabinet) ---
class Entreprise(models.Model):
    nom = models.CharField(max_length=150)
    siret = models.CharField(max_length=14, unique=True, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # On lie l'entreprise au compte utilisateur (Le Gérant)
    gerant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nom

# --- TABLE DES TRANSACTIONS ---
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('IN', 'Revenu'),
        ('OUT', 'Dépense'),
    ]
    
    # NOUVEAU : Chaque transaction appartient désormais à une entreprise !
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True)
    
    date = models.DateField()
    libelle = models.CharField(max_length=200)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.libelle} ({self.montant} €)"
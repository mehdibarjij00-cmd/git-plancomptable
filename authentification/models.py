from django.db import models
from django.contrib.auth.models import User

# --- TABLE DES PME ---
class Entreprise(models.Model):
    nom = models.CharField(max_length=150)
    siret = models.CharField(max_length=14, unique=True, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    gerant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nom

# --- TABLE DES TRANSACTIONS ---
class Transaction(models.Model):
    TYPE_CHOICES = [('IN', 'Revenu'), ('OUT', 'Dépense')]
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    libelle = models.CharField(max_length=200)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.libelle} ({self.montant} €)"

# --- TABLE DU PLAN COMPTABLE ---
class CompteComptable(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=150) # CHANGÉ : 'nom' devient 'libelle' pour être raccord avec views.py
    classe = models.IntegerField() 

    def __str__(self):
        return f"{self.numero} - {self.libelle}"

# --- TABLE DES ÉCRITURES COMPTABLES ---
class EcritureComptable(models.Model):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField()
    libelle = models.CharField(max_length=200)
    compte = models.ForeignKey(CompteComptable, on_delete=models.RESTRICT)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date} | {self.compte.numero} | D:{self.debit} C:{self.credit}"
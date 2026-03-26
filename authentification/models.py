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

# --------------------------------------------------------  

# comptabilite/models.py
# --- TABLE DU PLAN COMPTABLE ---
class CompteComptable(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=150)
    classe = models.IntegerField() # 1:Capitaux, 2:Immo, 3:Stocks, 4:Tiers, 5:Tréso, 6:Charges, 7:Produits

    def __str__(self):
        return f"{self.numero} - {self.nom}"

# --- TABLE DES ÉCRITURES COMPTABLES ---
class EcritureComptable(models.Model):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    date = models.DateField()
    libelle = models.CharField(max_length=200)
    compte = models.ForeignKey(CompteComptable, on_delete=models.RESTRICT)
    
    # En comptabilité, on utilise toujours le Débit et le Crédit séparément
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.date} | {self.compte.numero} | D:{self.debit} C:{self.credit}"
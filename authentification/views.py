import openpyxl
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime


# API Django pour l'authentification et le dashboard
from django.shortcuts import render, redirect # API Communication Web
from django.contrib.auth import authenticate, login, logout # API Sécurité et Identité
from django.contrib import messages # API messages pour les erreurs de connexion
from django.db.models import Sum # API d'Interface Utilisateur
from .models import Transaction, Entreprise, CompteComptable, EcritureComptable
# # def login_view(request):
#     if request.method == 'POST':
#         u = request.POST.get('username')
#         p = request.POST.get('password')
#         user = authenticate(request, username=u, password=p)
#         if user is not None:
#             login(request, user)
#             return redirect('dashboard')
#         else:
#             messages.error(request, "Identifiant ou mot de passe incorrect.")
#     return render(request, 'authentification.html')
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            # C'EST ICI QU'ON POSE LE CODE PYTHON
            # Cette API stocke le message qui sera lu par le JavaScript
            messages.error(request, "Identifiant ou mot de passe incorrect.")
            
    return render(request, 'authentification.html')

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # 1. On cherche si l'utilisateur connecté gère une entreprise
    entreprise = Entreprise.objects.filter(gerant=request.user).first()

    # 2. S'il a une entreprise, on calcule SES données
    if entreprise:
        transactions_query = Transaction.objects.filter(entreprise=entreprise)
        revenus = transactions_query.filter(type='IN').aggregate(Sum('montant'))['montant__sum'] or 0
        depenses = transactions_query.filter(type='OUT').aggregate(Sum('montant'))['montant__sum'] or 0
        transactions_list = transactions_query.order_by('-date')[:5]
    else:
        # S'il n'a pas d'entreprise (compte vide)
        revenus = 0
        depenses = 0
        transactions_list = []

    solde = revenus - depenses

    context = {
        'solde': solde,
        'revenus': revenus,
        'depenses': depenses,
        'transactions': transactions_list,
        'entreprise_nom': entreprise.nom if entreprise else "Aucune entreprise liée"
    }
    
    return render(request, 'dashboard.html', context)

    # # Calculs pour le journal comptable (exemple de données globales)
    # revenus = Transaction.objects.filter(type='IN').aggregate(Sum('montant'))['montant__sum'] or 0
    # depenses = Transaction.objects.filter(type='OUT').aggregate(Sum('montant'))['montant__sum'] or 0
    # solde = revenus - depenses

    # context = {
    #     'solde': solde,
    #     'revenus': revenus,
    #     'depenses': depenses,
    #     'transactions': Transaction.objects.all().order_by('-date')[:5]
    # }
    # return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('dashboard')


# 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        # On récupère les identifiants du formulaire HTML
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # --- MODE DEBUG : On affiche ce que Django reçoit ---
        print("=== TENTATIVE DE CONNEXION ===")
        print(f"Identifiant reçu : '{u}'")
        print(f"Mot de passe reçu : '{p}'")
        
        # Vérification dans la base de données
        user = authenticate(request, username=u, password=p)
        print(f"Résultat de l'authentification : {user}")
        print("==============================")
        # ----------------------------------------------------

        if user is not None:
            login(request, user)
            return redirect('dashboard') # Redirige vers le dashboard si OK
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
            
    return render(request, 'authentification.html')

def dashboard_view(request):
    # Sécurité : si l'utilisateur n'est pas connecté, retour au login
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html')



# --- API : SUPPRESSION ---
def delete_transaction(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        transaction = get_object_or_404(Transaction, id=id)
        transaction.delete()
        messages.success(request, "La transaction a été supprimée.")
    return redirect('dashboard')

# --- API : EXPORT EXCEL ---
def export_excel(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Création du fichier Excel en mémoire
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Transactions"

    # En-têtes de colonnes
    columns = ['Date', 'Libellé', 'Type', 'Montant']
    ws.append(columns)

    # Récupération des données depuis PostgreSQL / SQLite
    transactions = Transaction.objects.all().order_by('-date')
    for t in transactions:
        ws.append([t.date.strftime("%d/%m/%Y"), t.libelle, t.type, t.montant])

    # Préparation de la réponse HTTP pour forcer le téléchargement
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=transactions_export.xlsx'
    
    wb.save(response)
    return response

# --- API : IMPORT EXCEL ---
def import_excel(request):
    if request.method == 'POST' and request.user.is_authenticated:
        excel_file = request.FILES.get('excel_file')
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Le fichier n'est pas au format Excel valide.")
            return redirect('dashboard')

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active

            count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[1] and row[3]: 
                    Transaction.objects.create(
                        date=row[0] if row[0] else datetime.today().date(),
                        libelle=row[1],
                        type=row[2] if row[2] in ['IN', 'OUT'] else 'OUT',
                        montant=row[3]
                    )
                    count += 1
            
            messages.success(request, f"{count} transactions importées avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'importation : {str(e)}")
            
    return redirect('dashboard')


# api de synchronisation bancaire simulée 
import random
from datetime import timedelta
from django.utils import timezone

# ---  ---
def sync_bank_api(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    # On vérifie si l'utilisateur a une entreprise liée
    entreprise = Entreprise.objects.filter(gerant=request.user).first()
    
    if not entreprise:
        messages.error(request, "Erreur API : Aucune entreprise liée à votre compte pour la synchronisation.")
        return redirect('dashboard')

    # Liste de faux libellés réalistes pour simuler une banque
    libelles_out = ["Abonnement Logiciel SaaS", "Facture EDF", "Fournisseur Matériel", "Frais Bancaires", "Assurance PME", "Loyer Bureaux"]
    libelles_in = ["Règlement Client Dupont", "Virement Client A", "Paiement Facture #2026-04", "Remboursement URSSAF"]

    # Générer 5 transactions aléatoires simulées
    count = 0
    for _ in range(5):
        type_trans = random.choices(['IN', 'OUT'], weights=[0.4, 0.6])[0] # 60% de dépenses, 40% de revenus
        libelle = random.choice(libelles_in) if type_trans == 'IN' else random.choice(libelles_out)
        montant = round(random.uniform(50.0, 3000.0), 2)
        
        # Date aléatoire dans les 30 derniers jours
        random_days = random.randint(0, 30)
        date_trans = timezone.now().date() - timedelta(days=random_days)

        Transaction.objects.create(
            entreprise=entreprise,
            date=date_trans,
            libelle=f"[SYNC BANQUE] {libelle}",
            type=type_trans,
            montant=montant
        )
        count += 1

    messages.success(request, f"Connexion API Bancaire réussie : {count} nouvelles opérations synchronisées.")
    return redirect('dashboard')

# -----------------------------------------------------------------------
# AFFICHER LE MODULE COMPTABILITÉ ---
def comptabilite_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    entreprise, created = Entreprise.objects.get_or_create(
        gerant=request.user,
        defaults={'nom': f"Entreprise de {request.user.username}"}
    )

    ecritures = EcritureComptable.objects.filter(entreprise=entreprise).order_by('-date')
    comptes = CompteComptable.objects.all().order_by('numero')

    # Calcul du Résultat Net
    total_produits = ecritures.filter(compte__classe=7).aggregate(Sum('credit'))['credit__sum'] or 0
    total_charges = ecritures.filter(compte__classe=6).aggregate(Sum('debit'))['debit__sum'] or 0
    resultat_net = total_produits - total_charges

    #  Calcul de l'Actif (Classes 2, 3, 4, 5) -> Solde Débiteur
    actif_debits = ecritures.filter(compte__classe__in=[2, 3, 4, 5]).aggregate(Sum('debit'))['debit__sum'] or 0
    actif_credits = ecritures.filter(compte__classe__in=[2, 3, 4, 5]).aggregate(Sum('credit'))['credit__sum'] or 0
    total_actif = actif_debits - actif_credits

    #  Calcul du Passif (Classe 1) -> Solde Créditeur + Résultat Net
    passif_credits = ecritures.filter(compte__classe__in=[1]).aggregate(Sum('credit'))['credit__sum'] or 0
    passif_debits = ecritures.filter(compte__classe__in=[1]).aggregate(Sum('debit'))['debit__sum'] or 0
    total_passif = (passif_credits - passif_debits) + resultat_net

    context = {
        'ecritures': ecritures,
        'comptes': comptes,
        'resultat_net': resultat_net,
        'total_actif': total_actif,
        'total_passif': total_passif,
    }
    return render(request, 'comptabilite.html', context)

# ------------------------  AJOUTER UNE ÉCRITURE  --------------------------------------------------
def ajouter_ecriture(request):
    if request.method == 'POST' and request.user.is_authenticated:
        entreprise = Entreprise.objects.filter(gerant=request.user).first()
        
        if entreprise:
            date_ecriture = request.POST.get('date')
            libelle = request.POST.get('libelle')
            compte_id = request.POST.get('compte')
            
            debit = float(request.POST.get('debit') or 0.00)
            credit = float(request.POST.get('credit') or 0.00)

            compte = get_object_or_404(CompteComptable, id=compte_id)

            EcritureComptable.objects.create(
                entreprise=entreprise,
                date=date_ecriture,
                libelle=libelle,
                compte=compte,
                debit=debit,
                credit=credit
            )
            messages.success(request, "L'écriture a bien été enregistrée.")
            
    return redirect('comptabilite')


# -------------------------------suppression d'une ecriture----------------------------------
def supprimer_ecriture(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    # ------------verification des droits et autorisations ou bloquage de suppression----------------------
    if not request.user.is_superuser:
        # --------On envoie le message d'erreur personnalisé-----------
        messages.error(request, "Tu n'as pas le droit de suppression. Contacte l'administrateur.")
        return redirect('comptabilite')

    # -Si c'est un admin (superuser), autorisee de supp l'écriture
    ecriture = get_object_or_404(EcritureComptable, id=id)
    ecriture.delete()
    messages.success(request, "L'écriture a été supprimée avec succès.")
    
    return redirect('comptabilite')

# ---------------------------   importation exportation dans le journal   --------------------------------------------

def export_excel(request):
    if not request.user.is_authenticated:
        return redirect('login')

    #  On récupère l'entreprise de l'utilisateur
    entreprise = Entreprise.objects.filter(gerant=request.user).first()
    
    #  Création du fichier Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Journal General"

    #les en tetes conformes a mon tableau
    ws.append(['Date', 'N° Compte', 'Libelle', 'Debit', 'Credit'])

    # 3. Récupération des écritures de l'entreprise
    ecritures = EcritureComptable.objects.filter(entreprise=entreprise).order_by('-date')
    
    for e in ecritures:
        ws.append([
            e.date.strftime("%d/%m/%Y") if e.date else "", 
            e.compte.numero, 
            e.libelle, 
            e.debit, 
            e.credit
        ])

    # 4. Préparation de la réponse
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=journal_{request.user.username}.xlsx'
    wb.save(response)
    
    return response
# ---------------------------   IMPORTATION / EXPORTATION JOURNAL   --------------------------------------------
def import_excel(request):
    if request.method == 'POST' and request.user.is_authenticated:
        excel_file = request.FILES.get('excel_file')
        
        if not excel_file or not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Format invalide. Utilisez un fichier .xlsx")
            return redirect('comptabilite')

        try:
            entreprise = Entreprise.objects.filter(gerant=request.user).first()
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            ws = wb.active
            
            count = 0
            for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row): continue 

#- -------------------------------- CONVERTISSEUR DE DATE --------------------------------
                date_val = row[0]
                if isinstance(date_val, str):
                    try:
                        date_val = datetime.strptime(date_val, "%d/%m/%Y").date()
                    except ValueError:
                        pass

                num_compte = str(row[1]).strip() if row[1] else None
                compte = CompteComptable.objects.filter(numero=num_compte).first()
                
                if not compte:
                    messages.error(request, f"Ligne {i} : Le compte '{num_compte}' n'existe pas.")
                    continue

                val_debit = float(row[3]) if row[3] is not None else 0.0
                val_credit = float(row[4]) if row[4] is not None else 0.0

                EcritureComptable.objects.create(
                    entreprise=entreprise,
                    date=date_val if date_val else datetime.today().date(),
                    libelle=str(row[2]) if row[2] else "Import Excel",
                    compte=compte,
                    debit=val_debit,
                    credit=val_credit
                )
                count += 1
            
            if count > 0:
                messages.success(request, f"Importation réussie : {count} lignes ajoutées.")

        except Exception as e:
            # C'est ce bloc qui manquait et qui causait l'erreur !
            messages.error(request, f"Erreur technique lors de l'import : {str(e)}")
            
    return redirect('comptabilite')
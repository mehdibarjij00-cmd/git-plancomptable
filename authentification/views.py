import openpyxl
import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

# IMPORTS POUR LE PDF (ReportLab)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from .models import Transaction, Entreprise, CompteComptable, EcritureComptable

# ==========================================
# 1. AUTHENTIFICATION & DECONNEXION
# ==========================================

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    return render(request, 'authentification.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ==========================================
# 2. DASHBOARD (SOLDE & TRANSACTIONS)
# ==========================================

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    entreprise = Entreprise.objects.filter(gerant=request.user).first()

    if entreprise:
        transactions_query = Transaction.objects.filter(entreprise=entreprise)
        revenus = transactions_query.filter(type='IN').aggregate(Sum('montant'))['montant__sum'] or 0
        depenses = transactions_query.filter(type='OUT').aggregate(Sum('montant'))['montant__sum'] or 0
        transactions_list = transactions_query.order_by('-date')[:5]
    else:
        revenus = depenses = 0
        transactions_list = []

    context = {
        'solde': revenus - depenses,
        'revenus': revenus,
        'depenses': depenses,
        'transactions': transactions_list,
        'entreprise_nom': entreprise.nom if entreprise else "Aucune entreprise liée"
    }
    return render(request, 'dashboard.html', context)

# ==========================================
# 3. MODULE COMPTABILITÉ (JOURNAL & BILAN)
# ==========================================

def comptabilite_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # On récupère ou crée l'entreprise par défaut
    entreprise, created = Entreprise.objects.get_or_create(
        gerant=request.user,
        defaults={'nom': f"Entreprise de {request.user.username}"}
    )

    ecritures = EcritureComptable.objects.filter(entreprise=entreprise).order_by('-date')
    comptes = CompteComptable.objects.all().order_by('numero')

    # Calculs Bilan / Résultat
    total_produits = ecritures.filter(compte__classe=7).aggregate(Sum('credit'))['credit__sum'] or 0
    total_charges = ecritures.filter(compte__classe=6).aggregate(Sum('debit'))['debit__sum'] or 0
    resultat_net = total_produits - total_charges

    total_actif = (ecritures.filter(compte__classe__in=[2,3,4,5]).aggregate(Sum('debit'))['debit__sum'] or 0) - \
                  (ecritures.filter(compte__classe__in=[2,3,4,5]).aggregate(Sum('credit'))['credit__sum'] or 0)

    passif_c = ecritures.filter(compte__classe=1).aggregate(Sum('credit'))['credit__sum'] or 0
    passif_d = ecritures.filter(compte__classe=1).aggregate(Sum('debit'))['debit__sum'] or 0
    total_passif = (passif_c - passif_d) + resultat_net

    context = {
        'ecritures': ecritures,
        'comptes': comptes,
        'resultat_net': resultat_net,
        'total_actif': total_actif,
        'total_passif': total_passif,
    }
    return render(request, 'comptabilite.html', context)

def ajouter_ecriture(request):
    if request.method == 'POST' and request.user.is_authenticated:
        entreprise = Entreprise.objects.filter(gerant=request.user).first()
        if entreprise:
            EcritureComptable.objects.create(
                entreprise=entreprise,
                date=request.POST.get('date'),
                libelle=request.POST.get('libelle'),
                compte_id=request.POST.get('compte'),
                debit=float(request.POST.get('debit') or 0),
                credit=float(request.POST.get('credit') or 0)
            )
            messages.success(request, "L'écriture a bien été enregistrée.")
    return redirect('comptabilite')

def supprimer_ecriture(request, id):
    if not request.user.is_authenticated: return redirect('login')
    if not request.user.is_superuser:
        messages.error(request, "Tu n'as pas le droit de suppression.")
        return redirect('comptabilite')
    
    get_object_or_404(EcritureComptable, id=id).delete()
    messages.success(request, "L'écriture a été supprimée.")
    return redirect('comptabilite')

# ==========================================
# 4. IMPORTS / EXPORTS EXCEL
# ==========================================

def export_excel_compta(request):
    if not request.user.is_authenticated: return redirect('login')
    entreprise = Entreprise.objects.filter(gerant=request.user).first()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Date', 'N° Compte', 'Libelle', 'Debit', 'Credit'])

    for e in EcritureComptable.objects.filter(entreprise=entreprise).order_by('-date'):
        ws.append([e.date.strftime("%d/%m/%Y"), e.compte.numero, e.libelle, e.debit, e.credit])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=journal_{request.user.username}.xlsx'
    wb.save(response)
    return response

def import_excel_compta(request):
    if request.method == 'POST' and request.user.is_authenticated:
        excel_file = request.FILES.get('excel_file')
        if not excel_file or not excel_file.name.endswith('.xlsx'):
            messages.error(request, "Fichier invalide.")
            return redirect('comptabilite')

        try:
            entreprise = Entreprise.objects.filter(gerant=request.user).first()
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            ws = wb.active
            count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row): continue
                compte = CompteComptable.objects.filter(numero=str(row[1]).strip()).first()
                if compte:
                    EcritureComptable.objects.create(
                        entreprise=entreprise,
                        date=row[0] if isinstance(row[0], datetime) else datetime.today().date(),
                        libelle=str(row[2]), compte=compte, debit=float(row[3] or 0), credit=float(row[4] or 0)
                    )
                    count += 1
            messages.success(request, f"{count} lignes importées.")
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
    return redirect('comptabilite')

# ==========================================
# 5. GÉNÉRATION PDF (JUSTIFICATIF)
# ==========================================

def generer_facture_pdf(request, ecriture_id):
    ecriture = get_object_or_404(EcritureComptable, id=ecriture_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Justificatif_{ecriture.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(2 * cm, height - 2 * cm, "JUSTIFICATIF D'ÉCRITURES COMPTABLES")
    
    p.setFont("Helvetica", 11)
    p.drawString(2 * cm, height - 3.5 * cm, f"Entreprise : {ecriture.entreprise.nom}")
    p.drawString(2 * cm, height - 4 * cm, f"Date : {ecriture.date.strftime('%d/%m/%Y')}")
    p.line(2 * cm, height - 4.5 * cm, width - 2 * cm, height - 4.5 * cm)

    p.drawString(2 * cm, height - 6 * cm, f"Libellé : {ecriture.libelle}")
    p.drawString(2 * cm, height - 6.5 * cm, f"Compte : {ecriture.compte.numero} - {ecriture.compte.libelle}")
    
    montant = ecriture.debit if ecriture.debit > 0 else ecriture.credit
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2 * cm, height - 8 * cm, f"Montant Total : {montant} €")

    p.showPage()
    p.save()
    return response

# ==========================================
# 6. SYNC BANQUE (SIMULATION)
# ==========================================

def sync_bank_api(request):
    if not request.user.is_authenticated: return redirect('login')
    entreprise = Entreprise.objects.filter(gerant=request.user).first()
    if not entreprise: return redirect('dashboard')

    lib_out = ["Abonnement SaaS", "Facture EDF", "Fournisseur Matériel"]
    lib_in = ["Règlement Client Dupont", "Virement Client A"]

    for _ in range(3):
        t_type = random.choice(['IN', 'OUT'])
        Transaction.objects.create(
            entreprise=entreprise, date=timezone.now().date(),
            libelle=f"[SYNC] {random.choice(lib_in if t_type == 'IN' else lib_out)}",
            type=t_type, montant=round(random.uniform(100, 2000), 2)
        )
    messages.success(request, "Synchronisation bancaire réussie.")
    return redirect('dashboard')
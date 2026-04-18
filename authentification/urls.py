from django.contrib import admin
from django.urls import path
from authentification import views  # On importe tout depuis ton dossier authentification

urlpatterns = [
    # --- Administration ---
    path('admin/', admin.site.urls),

    # --- Authentification ---
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- Dashboard & Banques ---
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('sync-banque/', views.sync_bank_api, name='sync_bank_api'),
    
    # --- Module Comptabilité & Facturation ---
    path('comptabilite/', views.comptabilite_view, name='comptabilite'),
    path('facturation/', views.facturation_view, name='facturation'),
    path('ajouter_ecriture/', views.ajouter_ecriture, name='ajouter_ecriture'),
    path('supprimer_ecriture/<int:id>/', views.supprimer_ecriture, name='supprimer_ecriture'),
    
    # --- Imports / Exports ---
    path('export-compta/', views.export_excel_compta, name='export_excel'),
    path('import-compta/', views.import_excel_compta, name='import_excel'),
    
    # --- Documents PDF ---
    path('generer-facture/<int:ecriture_id>/', views.generer_facture_pdf, name='generer_facture_pdf'),
]
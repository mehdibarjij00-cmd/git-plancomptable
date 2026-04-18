from django.contrib import admin
from django.urls import path
from authentification import views 
# ==== path pour les vues d'authentification, dashboard, comptabilité et facturation ====
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('comptabilite/', views.comptabilite_view, name='comptabilite'),
    path('facturation/', views.facturation_view, name='facturation'),
    path('reporting/', views.reporting_view, name='reporting'),
    
    # --- ACTIONS FACTURATION ---
    path('ajouter_client/', views.ajouter_client, name='ajouter_client'),
    path('supprimer_facture/<int:id>/', views.supprimer_facture, name='supprimer_facture'),
    path('detail_facture/<int:id>/', views.detail_facture, name='detail_facture'),
    path('creer_facture/', views.creer_facture, name='creer_facture'),
    path('pdf_facture/<int:id>/', views.pdf_facture, name='pdf_facture'),
    
    # --- ACTIONS COMPTA ---
    path('ajouter_ecriture/', views.ajouter_ecriture, name='ajouter_ecriture'),
    path('supprimer_ecriture/<int:id>/', views.supprimer_ecriture, name='supprimer_ecriture'),
    path('export-compta/', views.export_excel_compta, name='export_excel'),
    path('import-compta/', views.import_excel_compta, name='import_excel'),
    path('generer-facture/<int:ecriture_id>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    path('sync-banque/', views.sync_bank_api, name='sync_bank_api'),
# administration  
path('administration/', views.administration_view, name='administration_custom'),
path('administration/ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
path('administration/modifier/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
path('administration/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
path('administration/ajouter-groupe/', views.ajouter_groupe, name='ajouter_groupe'),
path('administration/supprimer-groupe/<int:group_id>/', views.supprimer_groupe, name='supprimer_groupe'),
]

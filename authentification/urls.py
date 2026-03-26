from django.urls import path
from . import views

urlpatterns = [
    # --- AUTHENTIFICATION ---
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # --- COMPTABILITÉ (COEUR DU MÉTIER) ---
    path('comptabilite/', views.comptabilite_view, name='comptabilite'),
    path('comptabilite/ajouter/', views.ajouter_ecriture, name='ajouter_ecriture'),
    path('comptabilite/supprimer/<int:id>/', views.supprimer_ecriture, name='supprimer_ecriture'),

    # --- IMPORTS / EXPORTS & APIS ---
    path('export-excel/', views.export_excel, name='export_excel'),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('delete-transaction/<int:id>/', views.delete_transaction, name='delete_transaction'),
    path('sync-bank/', views.sync_bank_api, name='sync_bank'),
]
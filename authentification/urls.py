
# 
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login', views.login_view),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
# 
# 
from django.urls import path
from . import views

urlpatterns = [
    # Tes routes de base
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('sync-bank/', views.sync_bank_api, name='sync_bank'),
    
    # --- LES NOUVELLES ROUTES POUR LE DASHBOARD ---
    path('export-excel/', views.export_excel, name='export_excel'),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('delete/<int:id>/', views.delete_transaction, name='delete_transaction'),
]
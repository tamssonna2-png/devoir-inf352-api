from django.urls import path
from . import views

urlpatterns = [
    path('ajouter-utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('liste-utilisateurs/',views.liste_utilisateurs,name='liste_utilisateurs'),
    path('supprimer-utilisateur/<int:util_id>/',views.supprimer_utilisateur,name='supprimer_utilisateur'),
    path('modifier-utilisateur/<int:util_id>/',views.modifier_utilisateur,name='modifier_utilisateur'),
    path('creer-controleur/',views.creer_controleur,name='creer_controleur'),
    path('liste-controleur/',views.liste_controleur,name='liste_controleur'),
    path('supprimer-controleur/<int:contro_id>/',views.supprimer_controleur,name='supprimer_controleur'),
    path('modifier-controleur/<int:contro_id>/',views.modifier_controleur,name='modifier_controleur'),
    path('effectuer-transaction/',views.effectuer_transaction,name='effectuer_transaction'),
    path('afficher-solde/<int:util_id>/',views.afficher_solde,name='afficher_solde'),
]
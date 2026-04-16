from django.urls import path
from . import views

urlpatterns = [
    path('ajouter-utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('liste-utilisateurs/',views.liste_utilisateurs,name='liste_utilisateurs'),
]
from django.db import models

# Create your models here.
class Controleur(models.Model):
    nom = models.CharField(max_length=200)
    mot_de_passe = models.CharField(max_length=200)
    
class Utilisateur(models.Model):
    nom = models.CharField(max_length=200)
    mot_de_passe = models.CharField(max_length=200)
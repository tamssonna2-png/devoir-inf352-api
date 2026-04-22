from django.db import models

# Create your models here.
class Controleur(models.Model):
    nom = models.CharField(max_length=200)
    mot_de_passe = models.CharField(max_length=200)
    
class Utilisateur(models.Model):
    nom = models.CharField(max_length=200)
    mot_de_passe = models.CharField(max_length=200)
    solde = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
class Transaction(models.Model):
    TYPE_CHOICES = [('DEPOT', 'Dépôt'), ('RETRAIT', 'Retrait'),('VIREMENT','Virement')]
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='envois', null=True, blank=True)
    recepteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='receptions', null=True, blank=True)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
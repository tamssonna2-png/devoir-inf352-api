from rest_framework import serializers
from .models import Utilisateur,Controleur,Transaction

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['nom', 'mot_de_passe','solde']
        extra_kwargs = {
            'mot_de_passe': {
                #'write_only': True,
                'min_length':6,
                'help_text':'Le mot de passe doit contenir au moins 6 caractères'
            },
            'solde':{'read_only':True}
        }
        
class ControleurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Controleur
        fields = ['nom', 'mot_de_passe']
        
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'montant', 'type_transaction', 'date']
        
class TransactionInputSerializer(serializers.Serializer):
    type_transaction = serializers.ChoiceField(choices=['DEPOT', 'RETRAIT', 'VIREMENT'])
    montant = serializers.DecimalField(max_digits=15, decimal_places=2)
    expediteur_id = serializers.IntegerField(required=False)
    recepteur_id = serializers.IntegerField(required=False)
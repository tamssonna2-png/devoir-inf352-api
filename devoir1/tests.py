from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Utilisateur
from decimal import Decimal

class BankSystemEngineeringTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = Utilisateur.objects.create(nom="User1", mot_de_passe="123", solde=5000.00)
        self.u2 = Utilisateur.objects.create(nom="User2", mot_de_passe="456", solde=100.00)

    def test_virement_atomique(self):
        """Vérifie l'intégrité d'un virement entre deux comptes"""
        payload = {
            "type_transaction": "VIREMENT",
            "expediteur_id": self.u1.id,
            "recepteur_id": self.u2.id,
            "montant": 1000.00
        }
        response = self.client.post('/api/devoir1/effectuer-transaction/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Vérification des soldes après virement
        self.u1.refresh_from_db()
        self.u2.refresh_from_db()
        self.assertEqual(self.u1.solde, Decimal('4000.00'))
        self.assertEqual(self.u2.solde, Decimal('1100.00'))

    def test_securite_solde_insuffisant(self):
        """Vérifie que le système bloque un retrait supérieur au solde"""
        payload = {
            "type_transaction": "RETRAIT",
            "expediteur_id": self.u2.id,
            "montant": 500.00
        }
        response = self.client.post('/api/devoir1/effectuer-transaction/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.u2.refresh_from_db()
        self.assertEqual(self.u2.solde, Decimal('100.00')) # Le solde n'a pas bougé
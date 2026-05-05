from django.test import TestCase
from rest_framework.test import APIClient
from .models import Utilisateur, Controleur, Transaction
from decimal import Decimal


class UtilisateurViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = Utilisateur.objects.create(nom="User1", mot_de_passe="123", solde=5000.00)
        self.u2 = Utilisateur.objects.create(nom="User2", mot_de_passe="456", solde=100.00)

    # --- ajouter_utilisateur ---
    def test_ajouter_utilisateur_valide(self):
        r = self.client.post('/api/devoir1/ajouter-utilisateur/', {"nom": "User3", "mot_de_passe": "789", "solde": 0}, format='json')
        self.assertEqual(r.status_code, 201)

    def test_ajouter_utilisateur_invalide(self):
        # serializer.is_valid() == False → branche 400
        r = self.client.post('/api/devoir1/ajouter-utilisateur/', {}, format='json')
        self.assertEqual(r.status_code, 400)

    # --- modifier_utilisateur ---
    def test_modifier_utilisateur_valide(self):
        r = self.client.patch(f'/api/devoir1/modifier-utilisateur/{self.u1.id}/', {"nom": "User1_modifie"}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_modifier_utilisateur_invalide(self):
        # serializer.is_valid() == False
        r = self.client.patch(f'/api/devoir1/modifier-utilisateur/{self.u1.id}/', {"solde": "pas_un_nombre"}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_modifier_utilisateur_introuvable(self):
        # get_object_or_404 → 404
        r = self.client.patch('/api/devoir1/modifier-utilisateur/9999/', {"nom": "X"}, format='json')
        self.assertEqual(r.status_code, 404)

    # --- liste_utilisateurs ---
    def test_liste_utilisateurs(self):
        r = self.client.get('/api/devoir1/liste-utilisateurs/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.data), 2)

    # --- supprimer_utilisateur ---
    def test_supprimer_utilisateur_existant(self):
        r = self.client.delete(f'/api/devoir1/supprimer-utilisateur/{self.u1.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertIn("supprimé", r.data["message"])

    def test_supprimer_utilisateur_introuvable(self):
        r = self.client.delete('/api/devoir1/supprimer-utilisateur/9999/')
        self.assertEqual(r.status_code, 404)


class ControleurViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.c1 = Controleur.objects.create(nom="Ctrl1", mot_de_passe="abc")

    # --- creer_controleur ---
    def test_creer_controleur_valide(self):
        r = self.client.post('/api/devoir1/creer-controleur/', {"nom": "Ctrl2", "mot_de_passe": "def"}, format='json')
        self.assertEqual(r.status_code, 201)

    def test_creer_controleur_invalide(self):
        r = self.client.post('/api/devoir1/creer-controleur/', {}, format='json')
        self.assertEqual(r.status_code, 400)

    # --- modifier_controleur ---
    def test_modifier_controleur_valide(self):
        r = self.client.patch(f'/api/devoir1/modifier-controleur/{self.c1.id}/', {"nom": "Ctrl1_modifie"}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_modifier_controleur_invalide(self):
        r = self.client.patch(f'/api/devoir1/modifier-controleur/{self.c1.id}/', {"solde": "invalide"}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_modifier_controleur_introuvable(self):
        r = self.client.patch('/api/devoir1/modifier-controleur/9999/', {"nom": "X"}, format='json')
        self.assertEqual(r.status_code, 404)

    # --- liste_controleur ---
    def test_liste_controleur(self):
        r = self.client.get('/api/devoir1/liste-controleurs/')
        self.assertEqual(r.status_code, 200)

    # --- supprimer_controleur ---
    def test_supprimer_controleur_existant(self):
        r = self.client.delete(f'/api/devoir1/supprimer-controleur/{self.c1.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertIn("supprimé", r.data["message"])

    def test_supprimer_controleur_introuvable(self):
        r = self.client.delete('/api/devoir1/supprimer-controleur/9999/')
        self.assertEqual(r.status_code, 404)


class TransactionViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = Utilisateur.objects.create(nom="User1", mot_de_passe="123", solde=5000.00)
        self.u2 = Utilisateur.objects.create(nom="User2", mot_de_passe="456", solde=100.00)

    # --- Paramètres manquants ---
    def test_transaction_sans_type(self):
        # type_transaction manquant → branche "not type_t"
        r = self.client.post('/api/devoir1/effectuer-transaction/', {"montant": 100}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn("manquants", r.data["erreur"])

    def test_transaction_sans_montant(self):
        # montant manquant → branche "not data.get('montant')"
        r = self.client.post('/api/devoir1/effectuer-transaction/', {"type_transaction": "DEPOT"}, format='json')
        self.assertEqual(r.status_code, 400)

    # --- DEPOT ---
    def test_depot_reussi(self):
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "DEPOT", "recepteur_id": self.u1.id, "montant": 500}, format='json')
        self.assertEqual(r.status_code, 201)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.solde, Decimal("5500.00"))

    # --- RETRAIT ---
    def test_retrait_reussi(self):
        # branche solde suffisant
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "RETRAIT", "expediteur_id": self.u1.id, "montant": 500}, format='json')
        self.assertEqual(r.status_code, 201)
        self.u1.refresh_from_db()
        self.assertEqual(self.u1.solde, Decimal("4500.00"))

    def test_retrait_solde_insuffisant(self):
        # branche solde insuffisant (u2 a 100, retire 1000)
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "RETRAIT", "expediteur_id": self.u2.id, "montant": 1000}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn("insuffisant", r.data["erreur"])

    # --- VIREMENT ---
    def test_virement_reussi(self):
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "VIREMENT", "expediteur_id": self.u1.id,
             "recepteur_id": self.u2.id, "montant": 200}, format='json')
        self.assertEqual(r.status_code, 201)
        self.u1.refresh_from_db()
        self.u2.refresh_from_db()
        self.assertEqual(self.u1.solde, Decimal("4800.00"))
        self.assertEqual(self.u2.solde, Decimal("300.00"))

    def test_virement_sans_expediteur(self):
        # branche "not exp_id or not rec_id"
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "VIREMENT", "recepteur_id": self.u2.id, "montant": 100}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn("expéditeur", r.data["erreur"])

    def test_virement_sans_recepteur(self):
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "VIREMENT", "expediteur_id": self.u1.id, "montant": 100}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_virement_solde_insuffisant(self):
        # branche exp.solde < montant dans VIREMENT
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "VIREMENT", "expediteur_id": self.u2.id,
             "recepteur_id": self.u1.id, "montant": 9999}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn("insuffisant", r.data["erreur"])

    # --- Type inconnu ---
    def test_type_inconnu(self):
        # branche else finale
        r = self.client.post('/api/devoir1/effectuer-transaction/',
            {"type_transaction": "INCONNU", "montant": 100}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn("inconnu", r.data["erreur"])

    # --- afficher_solde ---
    def test_afficher_solde_existant(self):
        r = self.client.get(f'/api/devoir1/afficher-solde/{self.u1.id}/')
        self.assertEqual(r.status_code, 200)

    def test_afficher_solde_introuvable(self):
        r = self.client.get('/api/devoir1/afficher-solde/9999/')
        self.assertEqual(r.status_code, 404)


#instruction pour faire les test  d'instructions
#coverage run --source='.' manage.py test
#coverage html
#instruction pour le branch testing
#coverage run --branch --source='.' manage.py test
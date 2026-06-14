import uuid
import random
from django.core.management.base import BaseCommand
from django.db import models
from devoir1.models import Utilisateur, Controleur, Transaction  # Ajuste selon tes modèles

class Command(BaseCommand):
    help = "Peuple la base de données Neon avec des données de test (100+ lignes par table)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début du peuplement de la base de données..."))
        
        # Nettoyer les anciennes données (optionnel - commenter si tu veux conserver)
        self.clean_existing_data()

        # 1. Génération de 120 UTILISATEURS uniques
        self.stdout.write("\n📊 Création des utilisateurs...")
        utilisateurs_crees = []
        
        for i in range(1, 121):
            unique_id = str(uuid.uuid4())[:6]
            nom = f"Utilisateur_{i}_{unique_id}"
            mot_de_passe = f"Pass{i}123!"
            solde = random.uniform(0, 1000000)  # Solde entre 0 et 1 million
            
            utilisateur = Utilisateur.objects.create(
                nom=nom,
                mot_de_passe=mot_de_passe,
                solde=round(solde, 2)
            )
            utilisateurs_crees.append(utilisateur)
            
            if i % 20 == 0:
                self.stdout.write(f"  ✅ {i} utilisateurs créés...")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(utilisateurs_crees)} utilisateurs créés avec succès!"))

        # 2. Génération de 110 CONTROLEURS uniques
        self.stdout.write("\n👮 Génération des contrôleurs...")
        controleurs_crees = []
        
        roles = ["super_admin", "admin_financier", "moderateur", "validateur", "inspecteur"]
        
        for i in range(1, 111):
            unique_id = str(uuid.uuid4())[:6]
            nom = f"Controleur_{i}_{unique_id}"
            mot_de_passe = f"Ctrl{i}Secure@2024"
            
            controleur = Controleur.objects.create(
                nom=nom,
                mot_de_passe=mot_de_passe
            )
            controleurs_crees.append(controleur)
            
            if i % 20 == 0:
                self.stdout.write(f"  ✅ {i} contrôleurs créés...")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(controleurs_crees)} contrôleurs créés avec succès!"))

        # 3. Génération de 500+ TRANSACTIONS
        self.stdout.write("\n💰 Génération des transactions...")
        transactions_crees = []
        
        types_transaction = ['DEPOT', 'RETRAIT', 'VIREMENT']
        
        for i in range(1, 501):
            type_trans = random.choice(types_transaction)
            montant = round(random.uniform(10, 10000), 2)
            
            if type_trans == 'VIREMENT':
                # Virement entre deux utilisateurs différents
                expediteur = random.choice([u for u in utilisateurs_crees if u.solde >= montant])
                # S'assurer que le récepteur est différent
                recepteurs_possibles = [u for u in utilisateurs_crees if u.id != expediteur.id]
                if recepteurs_possibles:
                    recepteur = random.choice(recepteurs_possibles)
                    
                    # Mettre à jour les soldes
                    expediteur.solde -= montant
                    recepteur.solde += montant
                    expediteur.save()
                    recepteur.save()
                    
                    transaction = Transaction.objects.create(
                        expediteur=expediteur,
                        recepteur=recepteur,
                        montant=montant,
                        type_transaction=type_trans
                    )
                else:
                    continue
                    
            elif type_trans == 'DEPOT':
                # Dépôt (seulement récepteur)
                utilisateur = random.choice(utilisateurs_crees)
                utilisateur.solde += montant
                utilisateur.save()
                
                transaction = Transaction.objects.create(
                    expediteur=None,
                    recepteur=utilisateur,
                    montant=montant,
                    type_transaction=type_trans
                )
                
            else:  # RETRAIT
                # Retrait (seulement expediteur)
                utilisateur = random.choice([u for u in utilisateurs_crees if u.solde >= montant])
                utilisateur.solde -= montant
                utilisateur.save()
                
                transaction = Transaction.objects.create(
                    expediteur=utilisateur,
                    recepteur=None,
                    montant=montant,
                    type_transaction=type_trans
                )
            
            transactions_crees.append(transaction)
            
            if i % 50 == 0:
                self.stdout.write(f"  ✅ {i} transactions créées...")
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(transactions_crees)} transactions créées avec succès!"))

        # 4. Statistiques finales
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📈 RÉSUMÉ FINAL:"))
        self.stdout.write(f"  • Utilisateurs: {Utilisateur.objects.count()}")
        self.stdout.write(f"  • Contrôleurs: {Controleur.objects.count()}")
        self.stdout.write(f"  • Transactions: {Transaction.objects.count()}")
        
        # Afficher quelques statistiques supplémentaires
        total_soldes = Utilisateur.objects.aggregate(total=models.Sum('solde'))['total'] or 0
        self.stdout.write(f"  • Solde total des utilisateurs: {total_soldes:,.2f} FCFA")
        
        # Statistiques par type de transaction
        depots = Transaction.objects.filter(type_transaction='DEPOT').count()
        retraits = Transaction.objects.filter(type_transaction='RETRAIT').count()
        virements = Transaction.objects.filter(type_transaction='VIREMENT').count()
        
        self.stdout.write(f"  • Dépôts: {depots}")
        self.stdout.write(f"  • Retraits: {retraits}")
        self.stdout.write(f"  • Virements: {virements}")
        
        self.stdout.write("="*50)
        self.stdout.write(self.style.SUCCESS("🎉 Fin du peuplement avec succès !"))

    def clean_existing_data(self):
        """Optionnel: Nettoie les données existantes avant d'ajouter les nouvelles"""
        response = input("\n⚠️  Voulez-vous supprimer toutes les données existantes avant d'ajouter les nouvelles? (oui/non): ")
        
        if response.lower() == 'oui':
            self.stdout.write("🧹 Nettoyage des données existantes...")
            
            # Supprimer dans l'ordre inverse pour respecter les clés étrangères
            deleted_transactions = Transaction.objects.all().delete()
            deleted_controleurs = Controleur.objects.all().delete()
            deleted_utilisateurs = Utilisateur.objects.all().delete()
            
            self.stdout.write(f"  • Transactions supprimées: {deleted_transactions[0]}")
            self.stdout.write(f"  • Contrôleurs supprimés: {deleted_controleurs[0]}")
            self.stdout.write(f"  • Utilisateurs supprimés: {deleted_utilisateurs[0]}")
            self.stdout.write("✅ Nettoyage terminé!\n")
        else:
            self.stdout.write("📌 Conservation des données existantes, ajout de nouvelles données...\n")
            
"""📈 RÉSUMÉ FINAL:
  • Utilisateurs: 120
  • Contrôleurs: 110
  • Transactions: 500"""
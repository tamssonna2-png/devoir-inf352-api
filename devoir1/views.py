# Create your views here.
from decimal import Decimal  
from django.db import transaction      
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Utilisateur,Controleur,Transaction
from .serializers import UtilisateurSerializer,ControleurSerializer,TransactionSerializer,TransactionInputSerializer
from drf_spectacular.utils import extend_schema
# Create your views here.

@extend_schema(request=UtilisateurSerializer)
@api_view(['POST'])
def ajouter_utilisateur(request):
    serializer = UtilisateurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() 
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

 
@extend_schema(request=UtilisateurSerializer)
@api_view(['PUT','PATCH'])
def modifier_utilisateur(request,util_id):
    try:
        util = get_object_or_404(Utilisateur,id=util_id)
        serializer = UtilisateurSerializer(instance=util, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"erreur": str(e)}, status=500)
        
@api_view(['GET'])
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    serializer = UtilisateurSerializer(utilisateurs, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def supprimer_utilisateur(request,util_id):
    try:
        util = get_object_or_404(Utilisateur,id=util_id)
        util.delete()
        return Response({
            "message": f"{util.nom} supprimé(e)"
        })
    except Exception as e:
        return Response({"erreur":str(e)})

@extend_schema(request=ControleurSerializer)
@api_view(['POST'])
def creer_controleur(request):
    serializer = ControleurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@extend_schema(request=ControleurSerializer)
@api_view(['PUT','PATCH'])
def modifier_controleur(request,contro_id):
    try:
        contro = get_object_or_404(Controleur,id=contro_id)
        serializer = ControleurSerializer(instance=contro, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"erreur": str(e)}, status=500)

@api_view(['GET'])
def liste_controleur(request):
    controleur = Controleur.objects.all()
    serializer = ControleurSerializer(controleur, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def supprimer_controleur(request,contro_id):
    try:
        contro = get_object_or_404(Controleur,id=contro_id)
        contro.delete()
        return Response({
            "message": f"{contro.nom} supprimé(e)"
        })
    except Exception as e:
        return Response({"erreur":str(e)})




@extend_schema(request=TransactionInputSerializer)
@api_view(['POST'])
def effectuer_transaction(request):
    data = request.data
    type_t = data.get('type_transaction')
    
    # Validation de base
    if not type_t or not data.get('montant'):
        return Response({"erreur": "Paramètres manquants"}, status=400)
    
    try:
        montant = Decimal(str(data.get('montant')))
        with transaction.atomic():
            
            # --- CAS 1 : DEPOT (Seulement le recepteur) ---
            if type_t == 'DEPOT':
                util_id = data.get('recepteur_id') # L'ID de celui qui reçoit l'argent
                util = get_object_or_404(Utilisateur, id=util_id)
                util.solde += montant
                util.save()
                Transaction.objects.create(recepteur=util, montant=montant, type_transaction='DEPOT')

            # --- CAS 2 : RETRAIT (Seulement l'expediteur) ---
            elif type_t == 'RETRAIT':
                util_id = data.get('expediteur_id') # L'ID de celui qui retire
                util = get_object_or_404(Utilisateur, id=util_id)
                if util.solde < montant:
                    return Response({"erreur": "Solde insuffisant"}, status=400)
                util.solde -= montant
                util.save()
                Transaction.objects.create(expediteur=util, montant=montant, type_transaction='RETRAIT')

            # --- CAS 3 : VIREMENT (Les deux) ---
            elif type_t == 'VIREMENT':
                exp_id = data.get('expediteur_id')
                rec_id = data.get('recepteur_id')
                if not exp_id or not rec_id:
                    return Response({"erreur": "Besoin de l'expéditeur et du récepteur pour un virement"}, status=400)
                
                exp = get_object_or_404(Utilisateur, id=exp_id)
                rec = get_object_or_404(Utilisateur, id=rec_id)
                
                if exp.solde < montant:
                    return Response({"erreur": "Solde insuffisant"}, status=400)
                
                exp.solde -= montant
                rec.solde += montant
                exp.save()
                rec.save()
                Transaction.objects.create(expediteur=exp, recepteur=rec, montant=montant, type_transaction='VIREMENT')
            
            else:
                return Response({"erreur": "Type de transaction inconnu"}, status=400)

        return Response({"message": "Transaction effectuée avec succès"}, status=201)
    
    except Exception as e:
        return Response({"erreur": str(e)}, status=400)
    
@api_view(['GET'])
def afficher_solde(request,util_id):
    try:
        util=get_object_or_404(Utilisateur,id=util_id)
        return Response(util.solde)
    except Exception as e:
        return Response({"erreur":str(e)},statut=400)

#hey -n 10000 -c 100 http://127.0.0.1:8000/api/devoir1/liste-utilisateurs/
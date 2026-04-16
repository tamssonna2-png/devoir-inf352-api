# Create your views here.
        
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Utilisateur,Controleur
from .serializers import UtilisateurSerializer
from drf_spectacular.utils import extend_schema
# Create your views here.

@extend_schema(request=UtilisateurSerializer)
@api_view(['POST'])
def ajouter_utilisateur(request):
    serializer = UtilisateurSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() # Cela crée l'Utilisateur en base de données
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
    if request.method == 'POST':
        nom_recu = request.data.get('nom')
        mdp_recu = request.data.get('mot_de_passe')
        
        if not nom_recu or not mdp_recu:
            return Response({"erreur":"le nom et le mot de passe sont requis"},status=status.HTTP_400_BAD_REQUEST)
        
        nouvel_utilisateur = Utilisateur.objects.create(nom=nom_recu,mot_de_passe=mdp_recu)
        return Response({
            "message": "Utilisateur ajouté avec succès",
            "id": nouvel_utilisateur.id,
            "nom": nouvel_utilisateur.nom
        }, status=status.HTTP_201_CREATED)
   
        
@api_view(['GET'])
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    serializer = UtilisateurSerializer(utilisateurs, many=True)
    return Response(serializer.data)



# Trouver le bon équilibre
#hey -n 10000 -c 100 http://127.0.0.1:8000/api/devoir1/liste-utilisateurs/
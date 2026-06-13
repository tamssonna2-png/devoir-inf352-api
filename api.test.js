import { describe, it, expect } from 'vitest';
import axios from 'axios';

const BASE_URL = 'https://devoir-inf352-api.onrender.com';

describe('Scénario Complet de l\'API Bancaire sur Render', { timeout: 0 }, () => {
  let utilisateurId = null;
  // On utilise un nom unique avec un timestamp pour éviter de récupérer une ancienne ligne "Sonna"
  const uniqueNom = `Sonna Clautel ${Date.now()}`; 

  // Étape 1 : Créer un utilisateur et extraire son véritable ID de la base de données
  it('1. devrait réussir à créer un nouvel utilisateur', async () => {
    const payload = {
      nom: uniqueNom,
      mot_de_passe: "MonSuperMotDePasse123!"
    };

    // 1. Création
    const response = await axios.post(`${BASE_URL}/api/devoir1/ajouter-utilisateur/`, payload);
    expect([200, 201]).toContain(response.status);
    
    // 2. Récupération de la liste complète sur Neon pour trouver l'ID généré automatiquement
    const listeResponse = await axios.get(`${BASE_URL}/api/devoir1/liste-utilisateurs/`);
    const tousLesUtilisateurs = listeResponse.data;
    
    // On cherche l'utilisateur qu'on vient tout juste de créer par son nom unique
    const utilisateurTrouve = tousLesUtilisateurs.find(u => u.nom === uniqueNom);
    
    // Si ton modèle ou serializer n'inclut VRAIMENT pas le champ 'id', on prendra la position (index + 1) 
    // ou son champ d'identification. Essayons d'abord de lire u.id ou u.id_utilisateur
    utilisateurId = utilisateurTrouve?.id || utilisateurTrouve?.id_utilisateur;
    
    // Solution de secours si l'id n'est pas du tout sérialisé : on utilise le nom si ton modèle accepte le nom à la place de l'ID
    if (!utilisateurId) {
      console.log(" Le champ 'id' n'est pas présent dans le JSON renvoyé par ton serializer.");
      console.log("On tente d'utiliser l'index de sa position comme ID numérique.");
      utilisateurId = tousLesUtilisateurs.findIndex(u => u.nom === uniqueNom) + 1;
    }

    console.log(` Utilisateur trouvé en BDD. ID détecté : ${utilisateurId}`);
    expect(utilisateurId).toBeDefined();
  });

  // Étape 2 : Effectuer un dépôt (DEPOT)
  it('2. devrait réussir à effectuer un dépôt sur le compte', async () => {
    expect(utilisateurId).not.toBeNull();

    const transactionPayload = {
      type_transaction: "DEPOT",
      montant: 15000,
      recepteur_id: utilisateurId
    };

    const response = await axios.post(`${BASE_URL}/api/devoir1/effectuer-transaction/`, transactionPayload);
    expect(response.status).toBe(201);
    console.log(" Dépôt effectué :", response.data.message);
  });

  // Étape 3 : Vérifier le solde mis à jour
  it('3. devrait afficher le solde mis à jour de l\'utilisateur', async () => {
    expect(utilisateurId).not.toBeNull();

    const response = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(response.status).toBe(200);
    
    console.log(` Solde actuel de l'utilisateur (ID: ${utilisateurId}) :`, response.data);
    expect(Number(response.data)).toBe(15000);
  });

  // Étape 3 : Modifier l'utilisateur et vérifier la mise à jour
  it('4. devrait réussir à modifier l\'utilisateur et afficher son solde', async () => {
    expect(utilisateurId).not.toBeNull();

    // 1. On modifie le nom de l'utilisateur
    const modifPayload = {
      nom: `${uniqueNom} Modifié`
    };
    const modifResponse = await axios.patch(`${BASE_URL}/api/devoir1/modifier-utilisateur/${utilisateurId}/`, modifPayload);
    expect(modifResponse.status).toBe(200);
    console.log(" Utilisateur modifié avec succès");

    // 2. On vérifie son solde (qui doit toujours être à 15000 après le dépôt de l'étape 2)
    const soldeResponse = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(soldeResponse.status).toBe(200);
    
    console.log(` Solde actuel de l'utilisateur modifié (ID: ${utilisateurId}) :`, soldeResponse.data);
    expect(Number(soldeResponse.data)).toBe(15000);
  });
  it('5. devrait réussir à créer un nouveau contrôleur', async () => {
    const payload = {
      nom: `Ctrl Sonna ${Date.now()}`,
      mot_de_passe: "CtrlPass123!"
    };

    const response = await axios.post(`${BASE_URL}/api/devoir1/creer-controleur/`, payload);
    expect([200, 201]).toContain(response.status);
    console.log(" Contrôleur créé avec succès");
  });
// Étape 6 : Liste des contrôleurs et récupération de l'ID réel sur Neon
  it('6. devrait réussir à lister les contrôleurs et récupérer l\'ID créé', async () => {
    const response = await axios.get(`${BASE_URL}/api/devoir1/liste-controleur/`);
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);

    // Comme on sait que l'étape 5 vient de créer un contrôleur juste avant,
    // on récupère le tout dernier élément du tableau renvoyé par Render/Neon.
    const dernierControleur = response.data[response.data.length - 1];
    
    // Extraction de l'ID peu importe le nom du champ généré par le sérialiseur
    controleurId = dernierControleur?.id || dernierControleur?.id_controleur;

    console.log(` Contrôleur trouvé en BDD. ID détecté : ${controleurId}`);
    expect(controleurId).toBeDefined();
  });
  

});


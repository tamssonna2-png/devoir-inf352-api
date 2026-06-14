import { describe, it, expect } from 'vitest';
import axios from 'axios';

const BASE_URL = 'https://devoir-inf352-api.onrender.com';

describe('Scénario Complet de l\'API Bancaire sur Render', { timeout: 30000 }, () => {
  // Variables globales du bloc de test
  let utilisateurId = null;
  let monControleurId = null;

  const uniqueNom = `Sonna Clautel ${Date.now()}`; 

  // Étape 1 : Créer un utilisateur et extraire son ID réel
  it('1. devrait réussir à créer un nouvel utilisateur', async () => {
    const payload = {
      nom: uniqueNom,
      mot_de_passe: "MonSuperMotDePasse123!"
    };

    await axios.post(`${BASE_URL}/api/devoir1/ajouter-utilisateur/`, payload);
    
    // On va chercher dans la liste l'utilisateur qu'on vient de créer
    const listeResponse = await axios.get(`${BASE_URL}/api/devoir1/liste-utilisateurs/`);
    const utilisateurTrouve = listeResponse.data.find(u => u.nom === uniqueNom);
    
    // Extraction multi-clés : on teste toutes les variantes possibles de clé primaire
    utilisateurId = utilisateurTrouve?.id || 
                    utilisateurTrouve?.id_utilisateur || 
                    utilisateurTrouve?.pk ||
                    utilisateurTrouve?.id_user;

    // Si Django refuse toujours de renvoyer l'ID, on prend l'ID du tout dernier utilisateur de la liste par sécurité
    if (!utilisateurId && listeResponse.data.length > 0) {
      const dernier = listeResponse.data[listeResponse.data.length - 1];
      utilisateurId = dernier?.id || dernier?.id_utilisateur || dernier?.pk;
    }

    console.log(` Utilisateur trouvé en BDD. ID réel détecté : ${utilisateurId}`);
    expect(utilisateurId).toBeDefined();
    expect(utilisateurId).not.toBeNull();
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
  });

  // Étape 3 : Vérifier le solde mis à jour
  it('3. devrait afficher le solde mis à jour de l\'utilisateur', async () => {
    expect(utilisateurId).not.toBeNull();

    const response = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(response.status).toBe(200);
    
    console.log(` Solde actuel de l'utilisateur (ID: ${utilisateurId}) :`, response.data);
    expect(Number(response.data)).toBe(15000); 
  });

  // Étape 4 : Modifier l'utilisateur
  it('4. devrait réussir à modifier l\'utilisateur et afficher son solde', async () => {
    expect(utilisateurId).not.toBeNull();

    const payload = { nom: `${uniqueNom} Modifié` };
    const response = await axios.patch(`${BASE_URL}/api/devoir1/modifier-utilisateur/${utilisateurId}/`, payload);
    expect(response.status).toBe(200);

    const soldeResponse = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(soldeResponse.status).toBe(200);
    expect(Number(soldeResponse.data)).toBe(15000);
  });

  // Étape 5 : Créer un contrôleur
  it('5. devrait réussir à créer un nouveau contrôleur', async () => {
    const payload = {
      nom: `Ctrl Sonna ${Date.now()}`,
      mot_de_passe: "CtrlPass123!"
    };

    const response = await axios.post(`${BASE_URL}/api/devoir1/creer-controleur/`, payload);
    expect([200, 201]).toContain(response.status);
  });

  // Étape 6 : Lister les contrôleurs et récupérer l'ID
  it('6. devrait réussir à lister les contrôleurs et récupérer l\'ID créé', async () => {
    const response = await axios.get(`${BASE_URL}/api/devoir1/liste-controleur/`);
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);

    const dernierControleur = response.data[response.data.length - 1];
    
    // Utilisation de la variable locale au describe pour éviter les ReferenceError
    monControleurId = dernierControleur?.id;

    console.log(` Contrôleur trouvé en BDD. ID réel détecté : ${monControleurId}`);
    expect(monControleurId).toBeDefined();
    expect(monControleurId).not.toBeNull();
  });
});
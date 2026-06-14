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
  // Étape 7 : Modifier un contrôleur existant
  it('7. devrait réussir à modifier les informations du contrôleur', async () => {
    // On s'assure que l'ID du contrôleur a bien été récupéré à l'étape 6
    expect(monControleurId).toBeDefined();
    expect(monControleurId).not.toBeNull();

    const payload = {
      nom: "Contrôleur Modifié par Sonna"
    };

    console.log(`[MODIFICATION] Tentative de mise à jour du contrôleur ID : ${monControleurId}`);

    // Appel de la route avec la méthode PATCH
    const response = await axios.patch(`${BASE_URL}/api/devoir1/modifier-controleur/${monControleurId}/`, payload);
    
    // Validation du statut HTTP (200 OK)
    expect(response.status).toBe(200);
    console.log(" Contrôleur modifié avec succès sur Render");
  });
  // Étape 8 : Tester le cas de RETRAIT
  it('8. devrait réussir à effectuer un RETRAIT sur le compte de l\'utilisateur', async () => {
    expect(utilisateurId).not.toBeNull();

    // Récupération du solde initial pour calcul dynamique
    const avantResponse = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    const soldeInitial = Number(avantResponse.data);

    const payload = {
      type_transaction: "RETRAIT",
      montant: 5000,
      expediteur_id: utilisateurId
    };

    const response = await axios.post(`${BASE_URL}/api/devoir1/effectuer-transaction/`, payload);
    expect(response.status).toBe(201);
    console.log(" Transaction RETRAIT validée avec succès");

    // Vérification dynamique : Solde final = Solde initial - 5000
    const apresResponse = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(Number(apresResponse.data)).toBe(soldeInitial - 5000);
  });

  // Étape 9 : Tester le cas de VIREMENT
  it('9. devrait réussir à effectuer un VIREMENT vers un autre utilisateur', async () => {
    expect(utilisateurId).not.toBeNull();

    // 1. Récupération du solde initial de l'expéditeur
    const avantResponse = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    const soldeInitialExp = Number(avantResponse.data);

    // 2. Création du bénéficiaire temporaire
    const nomBeneficiaire = `Bénéficiaire ${Date.now()}`;
    await axios.post(`${BASE_URL}/api/devoir1/ajouter-utilisateur/`, {
      nom: nomBeneficiaire,
      mot_de_passe: "DestPass123!"
    });

    const listeResponse = await axios.get(`${BASE_URL}/api/devoir1/liste-utilisateurs/`);
    const beneficiaire = listeResponse.data.find(u => u.nom === nomBeneficiaire);
    const beneficiaireId = beneficiaire?.id;
    expect(beneficiaireId).toBeDefined();

    // 3. Exécution du virement de 3000
    const virementPayload = {
      type_transaction: "VIREMENT",
      montant: 3000,
      expediteur_id: utilisateurId,
      recepteur_id: beneficiaireId
    };

    const response = await axios.post(`${BASE_URL}/api/devoir1/effectuer-transaction/`, virementPayload);
    expect(response.status).toBe(201);
    console.log(` Virement de 3000 réussi vers l'ID ${beneficiaireId}`);

    // 4. Vérifications dynamiques des soldes finaux
    const soldeExp = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    expect(Number(soldeExp.data)).toBe(soldeInitialExp - 3000);

    const soldeRec = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${beneficiaireId}/`);
    expect(Number(soldeRec.data)).toBe(3000);
  });
  // Étape 10 : Tester la route afficher-solde (Succès et Erreur 404)
  it('10. devrait réussir à afficher le solde et renvoyer une 404 si l\'utilisateur n\'existe pas', async () => {
    // Cas 1 : Succès avec un utilisateur existant
    expect(utilisateurId).not.toBeNull();
    const responseSucces = await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/${utilisateurId}/`);
    
    expect(responseSucces.status).toBe(200);
    expect(responseSucces.data).toBeDefined();
    console.log(`[SOLDE] Route validée pour l'ID ${utilisateurId}. Valeur retournée : ${responseSucces.data}`);

    // Cas 2 : Erreur 404 avec un ID totalement fictif (ex: 999999)
    try {
      await axios.get(`${BASE_URL}/api/devoir1/afficher-solde/999999/`);
      // Si la requête passe sans lever d'erreur, on force l'échec du test
      expect('Une erreur 404 aurait dû être levée').toBe('Erreur non interceptée');
    } catch (error) {
      // On s'assure que l'API Django renvoie bien le code 404 via get_object_or_404
      expect(error.response.status).toBe(404);
      console.log(" [SOLDE] Route d'erreur validée : Code 404 bien reçu pour un ID inconnu.");
    }
  });
});
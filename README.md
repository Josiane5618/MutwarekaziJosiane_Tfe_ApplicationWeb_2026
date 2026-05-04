# Application Web de Gestion d'Accès

Ce projet a été réalisé dans le cadre de mon travail de fin d'études. L'objectif est de proposer une application web simple pour gérer l'accès à un bâtiment avec une vérification faciale, tout en permettant aussi la gestion des réservations de salles.

J'ai essayé de garder une application claire à comprendre, avec un backend séparé du frontend, une interface simple, et des fonctionnalités proches des diagrammes préparés pour le projet.

## Objectif Du Projet

L'application permet principalement de :

- inscrire un utilisateur avec une capture faciale
- faire valider ou refuser l'inscription par un administrateur
- connecter un utilisateur validé
- vérifier l'accès au bâtiment par reconnaissance faciale
- réserver, modifier et annuler une salle
- consulter ses notifications
- permettre à l'administrateur de gérer les demandes, les utilisateurs, les salles, les réservations et les logs d'accès

## Organisation Du Projet

Le projet est séparé en deux parties :

```text
backend/   API FastAPI, base de données, sécurité, reconnaissance faciale
frontend/  Interface React utilisée dans le navigateur
assets/    Modèles utilisés par la reconnaissance faciale
docs/local/ Documents personnels ignorés par Git
```

Le dossier `docs/local/` contient mes documents de travail locaux, par exemple les diagrammes et les consignes. Ce dossier est volontairement ignoré par Git.

## Fonctionnement Général

### Inscription

Un utilisateur non authentifié remplit le formulaire d'inscription et capture son visage avec la caméra. Le backend enregistre ses informations et stocke les données faciales nécessaires pour les vérifications futures.

Le compte reste en attente tant qu'un administrateur ne l'a pas validé.

### Validation Administrateur

L'administrateur se connecte avec le compte prévu pour l'administration. Il peut accepter ou refuser les demandes d'inscription.

Il peut aussi consulter et gérer :

- les utilisateurs
- les salles
- toutes les réservations
- les logs d'accès

### Accès Au Bâtiment

Une fois connecté, l'utilisateur peut demander l'accès au bâtiment. Il capture son visage, puis le backend compare cette capture avec les données enregistrées lors de l'inscription.

Le résultat peut être :

- `Accès autorisé`
- `Accès refusé`

Chaque tentative est enregistrée dans les logs d'accès. Le seuil actuel de comparaison faciale est fixé à `0.5` dans le backend. Plus la distance est basse, plus les deux visages sont considérés proches.

### Réservations

L'utilisateur connecté peut :

- consulter les salles disponibles
- créer une réservation
- modifier une réservation
- annuler une réservation
- consulter ses réservations

Le backend vérifie les conflits de créneaux pour éviter deux réservations au même moment dans la même salle.

### Profil Et Notifications

L'utilisateur peut mettre à jour son profil : prénom, nom, email et éventuellement son mot de passe.

Les notifications servent à informer l'utilisateur après certaines actions, comme une validation, une réservation ou une tentative d'accès.

## Lancer Le Projet

Il faut lancer le backend et le frontend dans deux terminaux séparés.

### Backend

```bash
cd backend
uv sync --extra face
uv run python run.py
```

L'API démarre normalement sur :

```text
http://127.0.0.1:8000
```

Vérification rapide :

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend démarre généralement sur :

```text
http://localhost:5173
```

Si ce port est déjà utilisé, Vite propose automatiquement un autre port.

## Configuration

La configuration sensible n'est pas écrite directement dans le code.

Les fichiers utilisés sont :

- `backend/.env`
- `frontend/.env`

Des exemples existent aussi avec :

- `backend/.env.example`
- `frontend/.env.example`

Dans mon environnement actuel, le backend utilise PostgreSQL sur le port `5433`.

## Compte Administrateur

Le compte administrateur local utilisé pendant le développement est :

```text
Email : admin@gestion-acces.dev
Mot de passe : Admin123!
```

Ce compte sert à valider les inscriptions et accéder au tableau de bord administrateur.

## Tests

Les tests backend peuvent être lancés avec :

```bash
cd backend
uv run pytest tests -q
```

Les tests couvrent notamment :

- l'inscription
- la connexion
- la validation administrateur
- la gestion des utilisateurs par l'administrateur
- la création, modification et annulation des réservations
- la consultation des logs et des réservations côté admin

## Utilisation Sous Windows

Le projet est prévu pour pouvoir fonctionner sous Windows, mais il faut recréer l'environnement Python sur la machine Windows.

Il ne faut pas copier un dossier `.venv` d'une autre machine.

Sous Windows, les commandes principales restent :

```powershell
cd backend
uv sync --extra face
uv run python run.py
```

Pour installer `uv` sous Windows :

```powershell
winget install --id=astral-sh.uv -e
```

La partie la plus sensible sous Windows est `dlib`, car cette dépendance peut parfois demander des outils natifs supplémentaires. Le reste du projet est plus classique.

## État Actuel

Aujourd'hui, l'application couvre les principaux cas prévus :

- inscription avec visage
- validation par l'administrateur
- connexion utilisateur
- accès bâtiment par reconnaissance faciale
- réservations de salles
- modification et annulation de réservations
- mise à jour du profil
- gestion administrateur des utilisateurs et des salles
- consultation des réservations et des logs d'accès

Il reste surtout à améliorer la présentation de certaines parties de l'interface, notamment le tableau de bord administrateur, pour qu'il soit plus agréable à utiliser pendant une démonstration.

## Points À Améliorer Plus Tard

- organiser le tableau administrateur avec des onglets
- améliorer encore les textes et l'ergonomie de l'interface
- préparer un jeu de données propre pour la démonstration
- ajouter une vraie stratégie de migration de base de données
- tester la reconnaissance faciale sur la machine Windows finale

## Remarque Personnelle

Ce projet a évolué progressivement. Au départ, certaines parties étaient seulement prévues dans les diagrammes. L'application est maintenant plus proche du fonctionnement attendu : l'utilisateur peut s'inscrire, être validé, réserver, modifier son profil et demander l'accès au bâtiment avec son visage.

Le but n'est pas d'avoir une application trop complexe, mais une base claire, démontrable et cohérente avec le sujet.

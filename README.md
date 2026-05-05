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

### Emails De Validation

Quand l'administrateur accepte ou refuse une inscription, le backend peut aussi envoyer un email.

Pour garder le projet simple pendant le développement, l'envoi SMTP est désactivé par défaut. Dans ce cas, l'email est affiché dans le terminal du backend.

Pour tester un vrai envoi local sans envoyer de vrais emails, on peut utiliser Mailpit :

```bash
mailpit
```

Mailpit reçoit les emails sur le port SMTP `1025` et permet de les voir dans le navigateur :

```text
http://127.0.0.1:8025
```

Dans `backend/.env`, il faut alors activer :

```env
SMTP_ENABLED=true
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@gestion-acces.dev
```

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

Les emails peuvent être testés localement avec Mailpit. Les variables principales sont :

- `SMTP_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_FROM_EMAIL`

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
- l'historique des demandes d'inscription
- l'envoi d'emails en mode local ou SMTP de test

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

## Bilan Par Rapport Aux Documents

Le projet a été rapproché du cahier des charges, du diagramme de cas d'utilisation et du diagramme de classes.

Les grandes fonctionnalités attendues sont présentes :

- inscription avec capture faciale
- validation ou refus par un administrateur
- email de réponse après décision administrateur
- connexion utilisateur
- réservation de salle avec règles de disponibilité
- annulation conservée dans l'historique
- accès au bâtiment par reconnaissance faciale
- logs d'accès
- tableau de bord administrateur

### Par Rapport Au Diagramme De Classes

Le code reprend les principales classes du diagramme, mais avec quelques adaptations liées au fonctionnement réel d'une API web.

Les classes bien représentées dans le backend sont :

- `Utilisateur`
- `Salle`
- `Reservation`
- `DonneeFaciale`
- `DemandeInscription`
- `Notification`
- `LogAcces`

Les énumérations du diagramme sont aussi représentées avec :

- `StatutCompte`
- `StatutDemandeInscription`
- `StatutReservation`
- `StatutSalle`
- `Role`, représenté dans le code par l'attribut `role` de `Utilisateur`

Les noms d'attributs sont proches, mais pas toujours exactement identiques.

Par exemple :

- le diagramme parle de `motDePasse`, le code utilise `mot_de_passe_hash`, car le mot de passe n'est jamais stocké en clair
- le diagramme parle de `statutCompte`, le code calcule `statut_compte` à partir du compte et de la demande d'inscription
- le diagramme parle de `dateSoumission` et `dateTraitement`, le code utilise `date_soumission` et `date_traitement`
- le diagramme parle de `heureDebut` et `heureFin`, le code utilise `heure_debut` et `heure_fin`
- le diagramme parle de `statutReservation`, le code utilise `statut`

Les fonctions du diagramme ne sont pas toutes codées comme des méthodes dans les classes. Dans l'application, elles sont surtout représentées par des routes API.

Par exemple :

- `s'authentifier()` correspond à `/auth/login`
- `consulterSalles()` correspond à `/reservations/salles`
- `consulterMesReservations()` correspond à `/reservations/mes-reservations`
- `modifierProfil()` correspond à `/auth/me`
- `demanderAcces()` correspond à `/access/verify`
- `traiterDemande()` correspond à `/admin/validate-user/{user_id}`
- `consulterLogsAcces()` correspond à `/admin/access-logs`
- `consulterToutesReservations()` correspond à `/admin/reservations`

La principale différence est la classe `Administrateur`. Dans le code, il n'y a pas une table séparée `Administrateur`. Un administrateur est un `Utilisateur` avec le rôle `admin`. C'est une simplification volontaire, car cela évite de dupliquer les informations communes comme le nom, l'email et le mot de passe.

Le diagramme de classes présente l'administrateur comme une spécialisation de l'utilisateur, mais il montre aussi une énumération `Role` avec les valeurs `UTILISATEUR` et `ADMINISTRATEUR`. Il y a donc déjà l'idée qu'un utilisateur possède un rôle. Dans le code, cette spécialisation est représentée par l'attribut `role`. Quand `role` vaut `admin`, l'utilisateur a accès aux routes d'administration.

Les actions propres à l'administrateur, comme traiter les demandes, consulter les logs ou gérer les salles, sont donc placées dans les routes `/admin`. Ces routes sont protégées et ne sont accessibles qu'aux comptes ayant le rôle `admin`.

Cette solution est plus simple pour une application web et garde la même logique métier : l'administrateur reste un utilisateur, mais avec plus de droits.

J'aurais pu créer une vraie classe `Administrateur` avec de l'héritage, mais cela aurait rendu la base de données et l'authentification plus compliquées. Pour ce projet, j'ai donc choisi une solution plus légère et plus facile à expliquer.

Le premier administrateur est créé automatiquement par le backend avec les variables de configuration. Il n'est pas créé par le formulaire public d'inscription.

### Points Encore Simplifiés

Quelques éléments restent volontairement simplifiés :

- il n'y a pas encore de vraie migration de base de données avec Alembic
- le tableau administrateur pourrait encore être organisé avec des onglets
- certains noms techniques suivent le style Python, donc `date_soumission` au lieu de `dateSoumission`
- la classe `Administrateur` est représentée par un rôle, pas par une table séparée
- les emails sont testables en local avec SMTP, mais pas configurés pour un service externe réel

Globalement, le code suit donc bien l'idée du diagramme de classes, mais il l'adapte à une architecture web plus simple : les données sont dans les modèles SQLAlchemy, et les actions sont dans les routes FastAPI.

## État Actuel

Aujourd'hui, l'application couvre les principaux cas prévus :

- inscription avec visage
- validation par l'administrateur
- connexion utilisateur
- accès bâtiment par reconnaissance faciale
- réservations de salles
- modification et annulation de réservations
- règles de réservation plus strictes
- mise à jour du profil
- demandes d'inscription avec statut et historique
- emails de validation en test local
- gestion administrateur des utilisateurs et des salles
- consultation des réservations et des logs d'accès
- consultation de la photo faciale par l'administrateur

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

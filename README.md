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

Le cahier des charges ne demandait pas explicitement la gestion des comptes administrateurs entre eux, mais j'ai préféré l'ajouter pour éviter qu'un seul administrateur bloque tout le système s'il perd son accès ou s'il oublie son mot de passe. L'administrateur peut donc aussi :

- promouvoir un utilisateur actif en administrateur
- retirer les droits d'un autre administrateur
- activer ou désactiver le compte d'un utilisateur

Pour ne pas créer de blocage, j'ai mis quelques garde-fous :

- un administrateur ne peut pas modifier son propre rôle ni désactiver son propre compte
- on ne peut pas retirer les droits du dernier administrateur actif
- seul un compte actif peut être promu administrateur

À chaque changement de rôle ou de statut, l'utilisateur concerné reçoit une notification dans l'application, et un email si l'envoi SMTP est activé.

### Accès Au Bâtiment

Une fois connecté, l'utilisateur peut demander l'accès au bâtiment. Il capture son visage, puis le backend compare cette capture avec les données enregistrées lors de l'inscription.

Le résultat peut être :

- `Accès autorisé`
- `Accès refusé`

Chaque tentative est enregistrée dans les logs d'accès. Le seuil actuel de comparaison faciale est fixé à `0.5` dans le backend. Plus la distance est basse, plus les deux visages sont considérés proches.

### Sécurité Des Données Biométriques

Le visage capturé pendant l'inscription est transformé par le backend en un vecteur de 128 nombres, ce qu'on appelle l'encodage facial. Cet encodage est une donnée biométrique sensible et ne doit pas pouvoir être lu directement dans la base de données.

Dans mon cahier des charges, je voulais garder pour ce projet la protection des données biométriques par chiffrement, déjà mise en place pendant le stage. J'ai donc choisi de chiffrer l'encodage facial avant de l'enregistrer, avec Fernet (fourni par la librairie `cryptography`), qui combine AES-128 et HMAC-SHA256.

La clé n'est pas écrite dans le code. Elle est lue depuis le fichier `backend/.env` à travers la variable `BIOMETRIC_ENCRYPTION_KEY`. Au démarrage de l'application, les anciens encodages qui étaient encore en clair sont chiffrés automatiquement, puis marqués comme tels grâce à la colonne `est_chiffre`.

Quand une comparaison faciale doit être faite, l'encodage est déchiffré en mémoire le temps du calcul, mais il n'est jamais réécrit en clair dans la base.

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

Mon cahier des charges prévoyait uniquement un envoi d'emails pour les décisions d'inscription, sans notification métier centrale. J'ai pourtant ajouté un système simple de notifications dans l'application : chaque utilisateur retrouve dans son tableau de bord les messages qui le concernent (validation de son inscription, réservation, tentative d'accès au bâtiment, changement de rôle ou de statut).

J'ai préféré cette solution parce que l'envoi SMTP n'est pas toujours activé pendant la démonstration. Une notification visible dans l'interface garantit que l'utilisateur voit toujours ce qui le concerne, même quand aucun email n'est envoyé.

### Emails Automatiques

Mon cahier des charges prévoyait l'envoi d'emails uniquement après acceptation ou refus d'une demande d'inscription. J'ai étendu cette logique à d'autres événements importants pour un système d'accès au bâtiment, parce qu'il m'a semblé utile que l'utilisateur soit prévenu chaque fois qu'une décision le concernant est prise.

Le backend peut donc envoyer un email automatique dans les cas suivants :

- acceptation ou refus d'une demande d'inscription (cas prévu par le cahier des charges)
- tentative d'accès au bâtiment (autorisée ou refusée)
- activation ou désactivation manuelle du compte par un administrateur
- changement de rôle (promotion ou rétrogradation administrateur)

Pour garder le projet simple pendant le développement, l'envoi SMTP est désactivé par défaut. Dans ce cas, l'email est affiché dans le terminal du backend.

Pour tester un vrai envoi local sans envoyer de vrais emails, on peut utiliser Mailpit. Sur Windows, j'ai préparé un script qui le lance avec la bonne configuration :

```powershell
.\start-mailpit.bat
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

Pour une démonstration, le scénario est simple :

1. lancer Mailpit
2. lancer le backend avec `SMTP_ENABLED=true`
3. lancer le frontend
4. inscrire un nouvel utilisateur
5. se connecter comme administrateur
6. accepter ou refuser la demande
7. ouvrir `http://127.0.0.1:8025` pour voir l'email reçu

Après la décision administrateur, l'interface affiche aussi si l'email a été envoyé vers SMTP ou seulement affiché dans le terminal.

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

Les emails peuvent être testés localement avec Mailpit. Les variables principales sont :

- `SMTP_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_FROM_EMAIL`

## Base De Données

L'application utilise PostgreSQL. Avant de lancer le backend pour la première fois, il faut :

1. installer PostgreSQL sur la machine
2. créer une base de données vide qui servira à l'application, par exemple `tfe_gestion_acces`
3. renseigner la chaîne de connexion dans `backend/.env`, via la variable `DATABASE_URL`

Le format de la chaîne de connexion est :

```text
DATABASE_URL=postgresql+psycopg://utilisateur:motdepasse@hote:port/nom_de_la_base
```

Dans mon environnement actuel, j'utilise PostgreSQL sur le port `5433` parce que le port `5432` était déjà occupé par une autre installation.

Au premier démarrage du backend, les tables sont créées automatiquement par le code, dans la fonction `bootstrap_database`. Les colonnes ajoutées plus tard sont également créées par le même mécanisme, ce qui évite d'avoir à exécuter des scripts SQL à la main. Cette approche reste simple, mais elle ne remplace pas une vraie stratégie de migration (voir « Points À Améliorer Plus Tard »).

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

Pour le frontend, il faut aussi avoir Node.js installé (version 22 ou plus). Sous Windows :

```powershell
winget install --id=OpenJS.NodeJS.LTS -e
```

Après l'installation, il peut être nécessaire de fermer puis rouvrir le terminal pour que `npm` soit reconnu.

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

Pour `Salle`, le code contient maintenant :

- `nom`, pour le nom court de la salle
- `description`, pour expliquer l'usage général de la salle
- `localisation`, pour indiquer le bâtiment, l'étage ou le numéro de local
- `equipements`, pour indiquer le matériel spécial disponible
- `capacite`, pour le nombre de personnes
- `active`, pour savoir si la salle est disponible dans l'application

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

La classe `Administrateur` du diagramme est représentée dans le code comme une spécialisation de `Utilisateur`. Concrètement, j'ai utilisé l'héritage de table unique (single-table inheritance) proposé par SQLAlchemy : il n'y a qu'une seule table `utilisateurs` en base de données, et la colonne `role` sert à distinguer un administrateur d'un utilisateur standard.

J'ai préféré cette solution plutôt qu'une table séparée parce qu'elle évite de dupliquer les informations communes (nom, email, mot de passe) et garde l'authentification simple : on cherche toujours dans la même table, puis on vérifie le rôle. Cela reste cohérent avec le diagramme, qui présente déjà une énumération `Role` avec les valeurs `UTILISATEUR` et `ADMINISTRATEUR`.

La classe `Administrateur` ajoute néanmoins les éléments spécifiques prévus par le diagramme :

- `niveau_acces` : permet de réserver la possibilité de différencier plus tard plusieurs niveaux d'administration
- `derniere_action` : conserve une trace simple de la dernière opération effectuée
- des méthodes métier comme `traiter_demandes`, `consulter_tous_logs`, `consulter_toutes_reservations`, `activer_desactiver_utilisateur` ou `gerer_salles`, qui reprennent les opérations attendues du diagramme

Dans la pratique, la plus grande partie de la logique reste portée par les routes FastAPI sous `/admin`, parce qu'une application web s'organise plus naturellement autour de ses routes que de ses méthodes de classe. Ces routes sont protégées et ne sont accessibles qu'aux comptes ayant le rôle `admin`.

Le premier administrateur est créé automatiquement par le backend avec les variables de configuration. Il n'est pas créé par le formulaire public d'inscription.

### Points Encore Simplifiés

Quelques éléments restent volontairement simplifiés :

- il n'y a pas encore de vraie migration de base de données avec Alembic
- certains noms techniques suivent le style Python, donc `date_soumission` au lieu de `dateSoumission`
- la classe `Administrateur` utilise l'héritage de table unique plutôt qu'une table séparée
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
- chiffrement des encodages faciaux en base de données
- promotion ou rétrogradation des administrateurs, avec garde-fous
- emails automatiques étendus aux tentatives d'accès et aux changements de compte

Il reste surtout à finir de soigner la présentation de certaines parties de l'interface.

## Points À Améliorer Plus Tard

- améliorer encore les textes et l'ergonomie de l'interface
- préparer un jeu de données propre pour la démonstration
- ajouter une vraie stratégie de migration de base de données
- tester la reconnaissance faciale sur la machine Windows finale

## Remarque Personnelle

Ce projet a évolué progressivement. Au départ, certaines parties étaient seulement prévues dans les diagrammes. L'application est maintenant plus proche du fonctionnement attendu : l'utilisateur peut s'inscrire, être validé, réserver, modifier son profil et demander l'accès au bâtiment avec son visage.

Le but n'est pas d'avoir une application trop complexe, mais une base claire, démontrable et cohérente avec le sujet.

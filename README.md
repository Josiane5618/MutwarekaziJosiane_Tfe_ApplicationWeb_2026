# Application Web 2026

Application de gestion d'acces avec :
- inscription utilisateur
- validation par un administrateur
- verification faciale
- reservations de salles
- notifications

J'ai organise ce projet de facon a garder une structure simple a suivre, avec un backend decoupe en `routers`, `models`, `schemas`, `security` et `utils`, et un frontend React volontairement leger. Certaines parties sont deja stables, d'autres sont encore en cours d'amelioration, donc ce README sert surtout a expliquer clairement comment le projet est construit et comment le lancer sans se perdre dans le code.

## Vue d'ensemble

Le depot contient deux applications :

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── routers/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── security/
│   │   └── utils/
│   ├── run.py
│   ├── test_face_recognition.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── README.md
└── assets/
    ├── dlib_face_recognition_resnet_model_v1.dat
    └── shape_predictor_68_face_landmarks.dat
```

## Stack technique

- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy
- Base de donnees: PostgreSQL
- Securite: JWT + hash mot de passe avec `passlib`
- Reconnaissance faciale: `dlib`, `opencv`, `numpy`

## Comment lire le code rapidement

Pour comprendre rapidement l'organisation du code, l'ordre de lecture suivant est le plus utile :

1. `backend/app/main.py`
2. `backend/app/routers/`
3. `backend/app/models/`
4. `backend/app/security/`
5. `frontend/src/App.jsx`
6. `frontend/src/components/RegisterForm.jsx`
7. `frontend/src/components/CameraCapture.jsx`
8. `frontend/src/api/api.js`

Cette sequence permet de partir des points d'entree, puis de descendre vers la logique et enfin vers les details techniques.

## Role de chaque dossier

### `backend/app/main.py`

Point d'entree FastAPI. Il cree l'application et branche les routes :
- `auth`
- `admin`
- `access`
- `reservation`
- `notification`
- `health`

### `backend/app/database.py`

Centralise la connexion a PostgreSQL et definit :
- `engine`
- `SessionLocal`
- `Base`

### `backend/app/dependencies.py`

Centralise les dependances partagees du backend, en particulier `get_db()` pour eviter de recopier la session SQLAlchemy dans chaque route.

### `backend/run.py`

Petit point d'entree pour demarrer l'API sans memoriser la commande `uvicorn`.

### `backend/app/models/`

Contient les tables principales :
- `Utilisateur`
- `DonneeFaciale`
- `Salle`
- `Reservation`
- `Notification`
- `LogAcces`

### `backend/app/routers/`

Contient la logique HTTP par domaine :
- `auth.py`: inscription et connexion
- `admin.py`: validation ou refus d'un compte
- `access.py`: verification faciale pour l'acces
- `reservation.py`: consultation des salles et creation de reservations
- `notification.py`: lecture des notifications

### `backend/app/security/`

Contient la logique d'authentification :
- creation du JWT
- verification du token
- controle du role administrateur
- hash et verification du mot de passe

### `backend/app/face_recognition/`

Contient le moteur de reconnaissance faciale. Le fichier `engine.py` charge les modeles `dlib` depuis `assets/` et extrait un vecteur facial a partir d'une image.

### `frontend/src/components/`

Composants React reutilisables :
- `CameraCapture.jsx`: active la webcam et capture une image
- `RegisterForm.jsx`: gere le formulaire d'inscription et envoie les donnees au backend

### `frontend/src/api/api.js`

Petit module d'acces HTTP. Il centralise les appels `fetch` vers le backend.

## Flux metier actuel

### 1. Inscription

L'idee du flux est la suivante :

1. l'utilisateur remplit le formulaire
2. il capture son visage
3. le frontend envoie les donnees au backend
4. le backend cree un utilisateur en attente
5. les donnees faciales sont stockees pour la verification future

### 2. Validation par l'administrateur

Un administrateur accepte ou refuse une demande d'inscription. Une notification email est simulee dans `backend/app/utils/email_service.py`.

### 3. Verification d'acces

Lors d'une tentative d'acces :

1. l'utilisateur envoie une nouvelle image
2. le backend extrait l'encodage facial
3. il compare cet encodage avec celui stocke en base
4. il enregistre un log
5. il cree une notification

### 4. Reservations et notifications

L'utilisateur authentifie peut :
- consulter les salles actives
- consulter ses reservations
- creer une reservation si le creneau est libre
- lire ses notifications

## Ce qui est bien structure aujourd'hui

- Le backend est deja decoupe par responsabilite, ce qui rend le code lisible.
- Les noms des dossiers sont simples et pedagogiques.
- Les routes metier sont separees par domaine fonctionnel.
- Le module `security/` isole bien les sujets JWT et mot de passe.
- Le frontend reste simple: peu de fichiers, peu d'abstraction inutile.
- Le moteur facial est isole dans un module dedie, ce qui evite de melanger cette logique avec les routes.

## Ce qui a ete stabilise

- l'inscription backend utilise maintenant une seule route cohérente avec le modele `Utilisateur`
- la validation admin repose sur `actif`
- la configuration sensible est sortie du code source
- le frontend affiche maintenant une vraie interface d'inscription
- la version de Node attendue est documentee et verifiee automatiquement
- le backend dispose maintenant d'un `requirements.txt`
- `get_db()` est centralise dans `backend/app/dependencies.py`

## Structure cible simple

L'objectif retenu ici est de garder une structure bien organisee mais facile a comprendre, avec cette logique :

- `models/`: uniquement la structure des tables
- `schemas/`: uniquement les entrees/sorties API
- `routers/`: uniquement la couche HTTP
- `services/`: logique metier reutilisable
- `security/`: auth et permissions
- `utils/`: helpers techniques

Le dossier `services/` n'est pas indispensable tout de suite. Il devient surtout pertinent si la logique d'inscription, de validation admin ou de verification faciale commence a grossir.

## Points de vigilance pour la suite

- ajouter une vraie strategie de migration de base de donnees
- ajouter des tests backend sur les routes principales
- remplacer le service email simule par une integration reelle si besoin
- verifier si un dossier `services/` devient utile quand la logique metier grossit
- nettoyer eventuellement l'historique du depot si `venv/` y a deja ete versionne

## Lancer le projet

## Configuration

La configuration n'est plus ecrite en dur dans le code.

- le backend lit en priorite `backend/.env`, puis `/.env` a la racine si besoin
- le frontend Vite lit `frontend/.env`

Des exemples sont fournis dans :
- `backend/.env.example`
- `frontend/.env.example`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Prerequis frontend :
- Node `20.19+` ou `22.12+`
- la version utilisee ici est `22.12.0`
- si `nvm` est installe, utiliser `nvm use` dans `frontend/`

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

L'API utilise les valeurs definies dans `backend/.env`.

Pour activer la reconnaissance faciale complete sur une machine qui supporte bien les dependances natives :

```bash
pip install -r requirements-face.txt
```

Verification rapide :

```bash
curl http://127.0.0.1:8000/health
```

## Utilisation sous Windows

Le projet peut etre utilise sous Windows, avec une attention particuliere sur la partie reconnaissance faciale.

### Frontend sous Windows

- installer Node `22.12.0`, ou plus largement `20.19+`
- ouvrir un terminal dans `frontend`
- lancer `npm install`
- lancer `npm run dev`

### Backend sous Windows

Dans PowerShell :

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Si PowerShell bloque l'activation du venv :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Verification rapide :

```powershell
curl http://127.0.0.1:8000/health
```

### Partie reconnaissance faciale sous Windows

- `opencv-python` est generalement plus simple a installer sur Windows car des wheels precompiles existent
- `dlib` est le point le plus sensible : selon la machine, il peut demander une compilation ou des outils natifs supplementaires
- `pip install -r requirements-face.txt` est donc a tester directement sur le PC Windows cible

Recommendation pratique :
- valider d'abord le backend standard avec `requirements.txt`
- ajouter ensuite `requirements-face.txt`
- ne pas copier un `.venv` Linux vers Windows
- recreer l'environnement Python directement sur le PC Windows

## Tests backend

Des tests simples ont ete ajoutes pour les routes les plus importantes :
- inscription
- connexion
- validation administrateur

Pour les lancer :

```bash
cd backend
pytest tests -q
```

## En resume

J'ai cherche a garder une base de code claire, simple et suffisamment robuste pour continuer le developpement sans ajouter de complexite inutile. L'architecture est maintenant plus coherente, la configuration est mieux isolee, le frontend est relie a un vrai flux d'inscription, et le backend peut se lancer et se tester plus facilement. La principale zone a surveiller reste la reconnaissance faciale native, surtout selon la machine cible, mais le reste du projet est maintenant plus propre et plus facile a reprendre.

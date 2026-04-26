# Frontend

Le frontend est une application React creee avec Vite.

## Role actuel

La partie interface sert surtout, pour l'instant, a preparer le flux d'inscription avec capture faciale :
- saisie des informations utilisateur
- activation de la webcam
- capture d'une image
- envoi des donnees au backend

## Fichiers importants

- `src/App.jsx` : point d'entree actuel de l'interface
- `src/components/RegisterForm.jsx` : formulaire d'inscription
- `src/components/CameraCapture.jsx` : capture webcam
- `src/api/api.js` : appels HTTP vers le backend

## Demarrage

```bash
npm install
npm run dev
```

## Configuration

Le frontend lit son URL backend depuis `frontend/.env` avec la variable :

```bash
VITE_API_URL=http://127.0.0.1:8000
```

Un exemple est fourni dans `frontend/.env.example`.

## Version de Node

Ce frontend utilise Vite 8. La version de Node retenue est `22.12.0`, ou plus generalement `20.19+` ou `22.12+`.

Le projet contient :

- `.nvmrc`
- `.node-version`
- une verification automatique avant `npm run dev`, `npm run build` et `npm run preview`

En cas d'erreur de version Node, l'environnement Node doit etre mis a jour avant de relancer les scripts.

Avec `nvm`, la sequence utilisee est :

```bash
nvm use
npm install
npm run dev
```

## Remarque

Le README principal du projet se trouve a la racine du depot dans `README.md`. C'est lui qui explique l'architecture globale backend + frontend.

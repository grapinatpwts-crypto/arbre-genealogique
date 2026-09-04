# Filiation — installation

Arbre généalogique collaboratif. Les données sont stockées dans **votre** projet
Firebase (Firestore). Un arbre n'est visible que par les comptes que son
propriétaire a invités, imposé par les Security Rules — il n'y a pas de serveur
applicatif entre le navigateur et la base.

## Architecture

```
 iPhone / Android          GitHub Pages              Firebase
 ┌──────────────┐          ┌────────────┐            ┌──────────────────────────┐
 │ PWA installée│ ────────▶│ index.html │ ──SDK─────▶│ Auth (Google)            │
 │ (icône)      │          │ (statique) │            │ Firestore                │
 └──────────────┘          └────────────┘            │  ↳ Security Rules        │
                                                     └──────────────────────────┘
```

Le fichier statique ne contient **aucune donnée**.

## Étape 1 — Le projet Firebase

1. [console.firebase.google.com](https://console.firebase.google.com) ▸ **Créer
   un projet**. Plan **Spark** (gratuit) suffit largement.
2. **Authentication ▸ Sign-in method** : activer le fournisseur **Google**.
3. **Firestore Database ▸ Créer une base** : mode production, région
   `europe-west9` (Paris).
4. **Authentication ▸ Settings ▸ Authorized domains** : ajouter le domaine
   d'hébergement (`votrepseudo.github.io`) et `localhost` pour tester en local.
5. **Paramètres du projet ▸ Général** : ajouter une application Web, copier
   l'objet de configuration (`apiKey`, `authDomain`, `projectId`…).

## Étape 2 — Déployer les règles et les index

Avec la [CLI Firebase](https://firebase.google.com/docs/cli)
(`npm install -g firebase-tools`, puis `firebase login`) :

```bash
firebase use --add
firebase deploy --only firestore:rules,firestore:indexes
```

`firestore.rules` porte toute la sécurité — à ne jamais déployer sans relire.
`firestore.indexes.json` déclare l'index composite de l'écran « Mes arbres ».

## Étape 3 — Renseigner la configuration côté client

Dans `index.html`, le module `<script type="module">` en tête de fichier :
remplacer l'objet passé à `initializeApp({...})` par celui copié à l'étape 1.
Ces valeurs sont publiques par nature — ce ne sont pas des secrets, la sécurité
tient aux Security Rules.

## Étape 4 — Héberger le front-end

Nouveau dépôt GitHub, y déposer `index.html`, `manifest.json`, `sw.js` et les
icônes, puis `Settings ▸ Pages ▸ Source : main / root`.

Icônes à fournir : `icon-192.png`, `icon-512.png`, `icon-512-maskable.png`
(fond `#F3EDE1`, marge de 12 % pour la version maskable).

## Étape 5 — Créer un arbre et inviter

Connectez-vous, créez un arbre : vous en êtes propriétaire. Membres & partage ▸
**Inviter** — l'adresse doit être exactement celle du compte Google de la
personne. Elle a accès dès sa première connexion, il n'y a pas d'acceptation à
donner.

## Étape 6 — Installer l'app sur téléphone

- **Android (Chrome)** : ouvrir le lien → bannière « Installer l'application ».
- **iPhone (Safari uniquement)** : Partager → « Sur l'écran d'accueil ».

## Sécurité — ce qui est en place

- Authentification Firebase (Google), cloisonnement par e-mail issu du jeton
- Toute la sécurité dans `firestore.rules` : le rôle est lu sur le document de
  l'arbre, jamais envoyé par le navigateur
- Trois rôles (propriétaire / éditeur / lecteur), le propriétaire ne pouvant pas
  se déclasser lui-même
- Tout ce qui n'est pas explicitement autorisé est refusé (`match /{document=**}`)

Documentation technique complète : [`PROJET.md`](PROJET.md).

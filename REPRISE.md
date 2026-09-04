# Reprise — où on en est, et par quoi continuer

Point d'entrée pour une nouvelle session. Le détail technique est dans
`PROJET.md`, les conventions de travail dans `CLAUDE.md`.

Dernière mise à jour : **5 septembre 2026**.

**Reprendre par** : écrire `index.html` (point 2 ci-dessous), après avoir tranché
la question de l'arbre initial — la base Firestore est vide, voir « L'arbre
initial n'existe pas encore ».

## Ce qui existe

| | État |
|---|---|
| Maquettes des 8 écrans | faites — canevas Claude Design, sources dans `design/*.dc.html` |
| Modèle de données | arrêté — `PROJET.md` § 3 |
| `firestore.rules` | écrit et **déployé** sur `filiation-vasseur` |
| `firestore.indexes.json`, `firebase.json` | écrits et déployés |
| `manifest.json`, `sw.js` | écrits |
| `index.html` | **n'existe pas** — c'est le gros du travail restant |
| Projet Firebase | **créé** — `filiation-vasseur`, Firestore `europe-west9` (Paris), Auth Google activée |
| Icônes PWA | **à créer** (`icon-192.png`, `icon-512.png`, `icon-512-maskable.png`) |

Canevas des maquettes : https://claude.ai/code/artifact/d6ff23ed-061d-4d17-b32e-c7724f28cf62

## Décisions prises, à ne pas rediscuter sans raison

- **Un seul arbre pour le moment** (4 sept. 2026). L'app s'ouvre directement sur
  la vue de l'arbre ; l'écran « Mes arbres » est dessiné mais pas construit. Le
  modèle garde quand même `arbres/{arbreId}` et ses sous-collections : ça ne
  coûte rien aujourd'hui et ça évite une migration le jour où il y en aura
  plusieurs. L'identifiant de l'arbre unique sera une constante en tête
  d'`index.html`.
- **La source est rattachée à l'événement, pas à la personne.** C'est l'acte qui
  atteste une date, pas la personne en général.
- **L'arbre entier se charge en mémoire.** Pas d'index par génération, pas de
  compteur dénormalisé. Limite assumée vers 2 000 personnes.
- **Charte papier d'archive** : crème `#F3EDE1`, encre `#1F1A14`, sanguine
  `#9A5233`, bleu d'archive `#3D5A8C` pour les sources. EB Garamond pour les
  noms, Archivo pour l'interface.

## Ce qui reste, dans l'ordre

1. **Retravailler la vue de l'arbre.** C'est le chantier design n° 1 : la
   maquette actuelle tient le principe (canevas de 720 px derrière un écran de
   390, bascule Ascendants / Descendants, sélection d'un cartouche) mais elle
   n'est pas au niveau. Tout le reste de l'app peut être construit sans
   attendre — c'est un écran, pas une fondation.
2. **Écrire `index.html`** : amorçage Firebase et `window.FB`, connexion Google,
   chargement complet de l'arbre en mémoire, puis les écrans dans cet ordre —
   vue de l'arbre, fiche, édition, rattachement, sources.
3. **Saisir les premières personnes** à partir des documents de Guillaume
   (voir ci-dessous).
4. Membres & partage — seulement quand il y aura quelqu'un à inviter.
5. Import GEDCOM — pas commencé, c'est ce qui permettra de récupérer un arbre
   existant depuis Geneanet.

*(Créer le projet Firebase et déployer règles et index : fait le 5 septembre 2026.)*

## L'arbre initial n'existe pas encore

La base est vide : aucun document `arbres/{arbreId}`. Or l'app s'ouvre
directement sur un arbre dont l'identifiant est une constante en tête
d'`index.html` — il faut donc que ce document existe, et qu'il porte le bon
e-mail comme propriétaire. Deux façons, à trancher :

- **Le créer à la main** dans la console Firestore. Les écritures console
  passent en admin, elles ignorent les règles : on choisit l'ID librement.
- **Le faire créer par `index.html`** à la première connexion, si l'arbre est
  absent. La règle `create` l'autorise, à condition que `membres` vaille
  exactement `[email]` et `roles` la seule clé `email → 'proprietaire'`.

**Attention à quel compte Google.** Les règles identifient par l'e-mail du
jeton, en minuscules. Le compte utilisé pour le CLI Firebase
(`grapinat.pwts@gmail.com`) n'est pas forcément celui avec lequel Guillaume se
connectera dans l'app. C'est ce dernier qui doit figurer comme `proprietaire`,
sinon la première lecture de l'arbre est refusée — et un refus de règle ne fait
aucun bruit, l'écran reste sur « Chargement… ».

## Configuration Firebase (à recopier dans `index.html` quand il sera écrit)

Projet `filiation-vasseur`, appli web « Arbre généalogique ». Valeurs publiques
par nature (voir `CLAUDE.md`), sans risque à les garder ici en clair.

```js
const firebaseConfig = {
  apiKey: "AIzaSyDsu6R8zTpcE83dA4JitWApEj5dNUVO3sY",
  authDomain: "filiation-vasseur.firebaseapp.com",
  projectId: "filiation-vasseur",
  storageBucket: "filiation-vasseur.firebasestorage.app",
  messagingSenderId: "677547453919",
  appId: "1:677547453919:web:f4b11142e2c179a709286a"
};
```

**Authentication ▸ Settings ▸ Domaines autorisés** contient déjà `localhost`,
`filiation-vasseur.firebaseapp.com` et `filiation-vasseur.web.app`. Il restera à
y ajouter `grapinatpwts-crypto.github.io` au moment d'activer GitHub Pages,
sinon la connexion Google échouera en ligne alors qu'elle marche en local.

## Ce qu'il faut de Guillaume pour avancer

- **Les photos des documents familiaux**, à fournir depuis son téléphone. Elles
  serviront à préciser les premières saisies : noms, dates, lieux, et surtout
  les **cotes** des actes, qui deviendront les sources.

### Comment traiter ces images quand elles arrivent

Ce sont des documents familiaux, pas des données de test : les lire, les
retranscrire, poser des questions sur ce qui est illisible — jamais deviner.
Une date qu'on n'arrive pas à lire reste vide, ou part dans `date_texte`
(« vers 1899 », « avant 1745 »), elle ne s'invente pas. Chaque information
transcrite d'un acte crée une **source** avec sa cote et pointe l'événement
qu'elle atteste. C'est le principe qu'on ne rediscute pas (voir `CLAUDE.md`).

Ne pas commiter les photos dans le dépôt : il est public, et ce sont des
documents de famille.

## Les deux pièges qui coûtent le plus cher

- **`git push` ne déploie pas `firestore.rules`.** Il faut
  `firebase deploy --only firestore:rules`. Le signaler dès que le fichier change.
- **Les clés de la map `roles` sont des e-mails**, donc
  `updateDoc({ ['roles.' + email]: 'editeur' })` découpe sur les points du
  domaine et écrit n'importe où. Il faut
  `setDoc(ref, { roles: { [email]: 'editeur' } }, { merge: true })`.

Les autres sont dans `PROJET.md` § 6.

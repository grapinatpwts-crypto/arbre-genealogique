# Reprise — où on en est, et par quoi continuer

Point d'entrée pour une nouvelle session. Le détail technique est dans
`PROJET.md`, les conventions de travail dans `CLAUDE.md`.

Dernière mise à jour : **5 septembre 2026**.

**Reprendre par** : ouvrir l'app et saisir le tableau 505A. `index.html` est
écrit ; ce qui reste à faire tient dans « Ce qui reste, dans l'ordre ».

## Ce qui existe

| | État |
|---|---|
| Maquettes des écrans | faites — canevas Claude Design, sources dans `design/*.dc.html` |
| Vue « Lignée » (parchemin) | maquette `design/VueArbre.dc.html`, spec `DESIGN-LIGNEE.md`, **portée dans l'app** |
| Modèle de données | arrêté — `PROJET.md` § 3 |
| `firestore.rules` | écrit et **déployé** sur `filiation-vasseur` |
| `firestore.indexes.json`, `firebase.json` | écrits et déployés |
| `manifest.json`, `sw.js` | écrits |
| `index.html` | **écrit** — connexion, arbre, fiche, édition, rattachement, sources |
| Projet Firebase | **créé** — `filiation-vasseur`, Firestore `europe-west9` (Paris), Auth Google activée |
| Icônes PWA | **faites** — générées depuis le glyphe de l'écran de connexion |
| GitHub Pages | **actif** — https://grapinatpwts-crypto.github.io/arbre-genealogique/ |

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

1. ~~Activer GitHub Pages et ajouter le domaine dans Firebase~~ — fait le
   5 septembre 2026. L'app est en ligne :
   https://grapinatpwts-crypto.github.io/arbre-genealogique/
2. **Importer la page 1 du tableau 505A** : 15 personnes, 1 conjoint, 8 unions.
   L'écran d'import existe — menu ⋯ de la vue de l'arbre, format dans
   `PROJET.md` § 6 — et le collage est prêt. Puis les pages 2 à 9, qui se
   raccordent à celle-ci par une ligne `ALIAS`.

   Le collage ne vit pas dans ce dépôt : il est public, et ce sont des données
   familiales, dont une personne vivante.
3. ~~Retravailler la vue de l'arbre~~ — fait le 5 septembre 2026. C'est
   maintenant la vue **Lignée** : un parchemin qui défile, sans cartouche, où la
   main qui écrit dit le siècle. Elle vient de la maquette `VueArbre.dc.html` et
   de sa spécification `DESIGN-LIGNEE.md`, dont le § 11 liste les écarts que les
   vraies données ont imposés. Reste à faire porter les **lacunes** par le modèle
   (« registres détruits en 1793 ») : le rendu existe, l'information non.
4. **Membres & partage** — l'écran est dessiné, pas construit ; il le sera quand
   il y aura quelqu'un à inviter.
5. **Import GEDCOM** — pas commencé, c'est ce qui permettra de récupérer un arbre
   existant depuis Geneanet.

*(Créer le projet Firebase et déployer règles et index : fait le 5 septembre
2026. Écrire `index.html` et les icônes : fait le 5 septembre 2026.)*

## L'arbre initial se crée tout seul

C'est la deuxième option qui a été retenue : à la première connexion,
`index.html` regarde si `arbres/principal` existe et le crée sinon, avec
`membres: [email]` et `roles: { email: 'proprietaire' }` — exactement la forme
que la règle `create` exige. Rien à faire à la main dans la console.

L'identifiant de l'arbre est la constante `ARBRE_ID` en tête d'`index.html`. Il
vaut `principal` et non un patronyme : il n'y a qu'un arbre, et le jour où il y
en aura plusieurs, celui-ci n'aura pas à être renommé.

**Le propriétaire est `grapinat.pwts@gmail.com`** (tranché le 5 septembre
2026) — le même compte que le CLI Firebase. Les autres membres seront ajoutés
depuis l'app, en lecteur / éditeur / propriétaire.

Les règles identifient par l'e-mail du jeton, en minuscules : si le
`proprietaire` de l'arbre n'est pas exactement le compte utilisé pour se
connecter, la première lecture est refusée — et un refus de règle ne fait aucun
bruit, l'écran reste sur « Chargement… ».

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

## Les documents de Guillaume

**Reçu le 5 septembre 2026 : le « Tableau d'ascendance n° 505A », page 1.** Une
feuille manuscrite en numérotation Sosa — on part du bas (n° 1, la personne de
référence) et on remonte, le père de `n` portant le n° `2n` et la mère `2n+1`.
Le second chiffre en tête de la ligne du haut est le **numéro de page** où
l'ascendance de cette personne continue ; il ne se stocke pas. Légende de la
feuille : `°` naissance, `†` décès, `□` inhumation, `x` mariage.

Cette page donne **15 ancêtres (Sosa 1 à 15) + 1 conjoint, et 8 unions**, jusqu'aux
arrière-grands-parents ; les pages 2 à 9 continuent chacune des huit branches.
La transcription est faite et relue avec Guillaume, mais elle **ne vit pas dans
ce dépôt** — il est public et il s'agit de données familiales, dont une personne
vivante. Elle reste sur le poste, à côté des photos.

C'est ce tableau qui a fait ajouter `inhumation` au modèle (voir `PROJET.md` § 3).

**Restent à obtenir :**

- **Les cotes des actes détenus.** La feuille surligne en rose, sous la mention
  « Actes détenus », les événements dont Guillaume possède l'acte. Ce sont eux
  qui deviendront les vraies sources. Question posée, pas encore tranchée : est-ce
  bien le sens du rose, et les cotes existent-elles déjà quelque part ?
- **Les pages 2 à 9** du tableau 505A, et les autres documents familiaux.

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

Les autres sont dans `PROJET.md` § 7.

# Filiation — documentation technique

App d'arbre généalogique **collaboratif**, avec sources d'archives rattachées
aux événements. PWA statique servie par GitHub Pages, qui parle directement à
Firestore depuis le navigateur. Pas de serveur applicatif, pas de Cloud
Function : toute la sécurité tient dans `firestore.rules`.

État au 4 septembre 2026 : **les maquettes et l'architecture existent,
`index.html` reste à écrire.** Voir `REPRISE.md`.

**Un seul arbre pour le moment** : l'app s'ouvrira directement sur la vue de
l'arbre, son identifiant étant une constante en tête d'`index.html`. Le modèle
ci-dessous reste multi-arbres — il ne coûte rien de plus et évite une migration.

## 1. Ce que fait l'app

Saisir une famille — personnes, filiations, unions — puis la visualiser sous
forme d'arbre, en ascendance ou en descendance, depuis n'importe qui. Chaque
date et chaque lieu peut porter la **source** qui l'atteste : acte d'état civil,
registre paroissial, recensement, relevé en ligne. C'est ce qui distingue l'app
d'un carnet : on sait toujours d'où vient l'information.

Plusieurs membres de la famille travaillent sur le même arbre, avec trois rôles.

## 2. Architecture

```
 iPhone / Android          GitHub Pages              Firebase
 ┌──────────────┐          ┌────────────┐            ┌──────────────────────────┐
 │ PWA installée│ ────────▶│ index.html │ ──SDK─────▶│ Auth (Google)            │
 │ (icône)      │          │ (statique) │            │ Firestore                │
 └──────────────┘          └────────────┘            │  ↳ Security Rules        │
                                                     └──────────────────────────┘
```

Reprise à l'identique de `coaching-musculation` : monolithe `index.html`
(HTML + CSS + JS inline), un module ES en tête de fichier qui importe le SDK
Firebase et l'expose sur `window.FB`, `persistentLocalCache` pour le hors-ligne,
`sw.js` avec un `CACHE` à incrémenter à chaque mise en ligne.

**L'arbre entier tient en mémoire.** Un arbre familial dépasse rarement quelques
milliers de personnes : l'app charge toutes les `personnes` et toutes les
`unions` d'un arbre en une fois, puis calcule ascendance, descendance, fratries
et compteurs de sources côté client. Ça supprime d'un coup les index composites,
les compteurs dénormalisés qui dérivent, et les requêtes par génération. Limite
assumée, à surveiller au-delà de ~2 000 personnes (voir § 6).

## 3. Modèle de données

Tout vit sous l'arbre : le contrôle d'accès se lit alors en **un seul `get()`**
sur le document de l'arbre, quelle que soit la profondeur.

### `arbres/{arbreId}`

| Champ | Type | Rôle |
|---|---|---|
| `nom` | string | « Famille Vasseur — Prigent » |
| `membres` | array\<email\> | sert à la requête `array-contains` de l'écran Mes arbres |
| `roles` | map email → rôle | `proprietaire` \| `editeur` \| `lecteur` |
| `invites` | array\<email\> | membres qui ne se sont jamais connectés (badge « en attente ») |
| `resume` | map | `{ personnes, sources }`, compteurs d'en-tête |
| `cree_par`, `cree_le`, `maj_par`, `maj_le` | | |

`membres` et `roles` disent la même chose deux fois, et c'est voulu : les règles
lisent le rôle dans la map, la requête de liste a besoin d'un tableau —
Firestore ne sait pas interroger les clés d'une map.

### `arbres/{arbreId}/personnes/{personneId}`

| Champ | Type | Rôle |
|---|---|---|
| `nom`, `nom_naissance`, `prenoms` | string | `nom_naissance` vide = identique à `nom` |
| `sexe` | `'M'` \| `'F'` \| `'?'` | |
| `naissance`, `deces` | map | `{ date, date_texte, lieu, sources: [sourceId] }` |
| `parents` | array\<personneId\> | 0 à 2 entrées — c'est **l'enfant** qui porte le lien |
| `profession`, `notes` | string | |
| `cree_par`, `cree_le`, `maj_par`, `maj_le` | | |

`date` est une chaîne `AAAA-MM-JJ`, jamais un `Timestamp` : une date d'état
civil est une date seule, pas un instant (voir § 6). `date_texte` porte
l'imprécision réelle des archives — « vers 1899 », « avant 1745 », « an VII » —
qui n'entre dans aucun format.

Le lien de filiation est porté par l'enfant, dans `parents`. Remonter une
ascendance est alors un simple parcours ; la descendance se calcule par index
inverse en mémoire, au chargement.

### `arbres/{arbreId}/unions/{unionId}`

`conjoints: [personneId, personneId]`, `mariage: { date, date_texte, lieu,
sources: [] }`, `divorce` (même forme ou `null`). Une union n'est pas la liste
des enfants : les enfants pointent leurs parents eux-mêmes, l'union ne sert
qu'à porter l'**événement** mariage et ses sources.

### `arbres/{arbreId}/sources/{sourceId}`

`titre`, `type` (`etat-civil` \| `paroissial` \| `recensement` \| `en-ligne` \|
`autre`), `cote` (« AD 49, 5 Mi 1234, vue 41 — acte n° 112 »), `url`, `notes`.

**La source est rattachée à l'événement, pas à la personne.** C'est l'acte n° 112
qui atteste la naissance du 14 mars 1929 — pas Marcel Vasseur en général. Le
rattachement vit donc dans `naissance.sources`, `deces.sources`,
`mariage.sources` : un tableau d'identifiants. Le compte inverse (« rattachée à
4 événements ») se calcule en mémoire, il n'est stocké nulle part et ne peut
donc pas dériver.

## 4. Rôles et partage

| Rôle | Peut |
|---|---|
| `proprietaire` | tout, plus inviter, changer les rôles, supprimer l'arbre |
| `editeur` | créer et modifier personnes, unions, sources ; renommer l'arbre |
| `lecteur` | consulter, rien d'autre |

L'invitation ajoute l'e-mail **tout de suite** dans `membres` et `roles` : la
personne a accès dès sa première connexion Google, il n'y a pas d'acceptation à
gérer. `invites` ne sert qu'à afficher « en attente » tant qu'elle ne s'est
jamais connectée. Le propriétaire ne peut pas se déclasser lui-même — les règles
le refusent, sinon un arbre pourrait se retrouver sans personne pour attribuer
les rôles.

## 5. Écrans

Maquettes cliquables : canevas Claude Design, sources dans `design/*.dc.html`.

1. **Connexion** — Google uniquement.
2. **Mes arbres** — liste par `array-contains`, rôle et compteurs. *Dessiné,
   pas construit : un seul arbre pour le moment.*
3. **Vue de l'arbre** — canevas pan/zoom, bascule Ascendants / Descendants,
   sélection d'un cartouche, recentrage sur n'importe qui. *La maquette tient le
   principe mais doit être retravaillée : c'est le chantier design n° 1.*
4. **Fiche d'une personne** — onglets Fiche / Famille / Sources.
5. **Édition** — formulaire ; le bloc Décès n'existe que si la personne l'est.
6. **Rattacher** — on choisit d'abord le lien (père, mère, conjoint, enfant,
   fratrie), puis la personne : existante ou créée dans la foulée.
7. **Membres & partage** — invitation par e-mail, changement de rôle.
8. **Sources** — liste filtrable par type d'acte.

## 6. Pièges — à lire avant de reprendre

- **`git push` ne déploie pas les règles.** `firebase deploy --only
  firestore:rules` est une commande à part. Un correctif de règles resté en
  local donne l'illusion que le bug est corrigé alors que le refus serveur
  persiste. Le signaler dès que `firestore.rules` change.
- **Une clé de map ne peut pas contenir de point avec `updateDoc`.** Les clés de
  `roles` sont des e-mails. `updateDoc(ref, { ['roles.' + email]: 'editeur' })`
  découpe sur les points du domaine et écrit n'importe où. Il faut
  `setDoc(ref, { roles: { [email]: 'editeur' } }, { merge: true })`, qui fusionne
  la map sans la réécrire.
- **Une date seule n'est pas un instant.** `new Date('1929-03-14')` donne minuit
  UTC. Les dates d'état civil restent des chaînes `AAAA-MM-JJ`, comparées comme
  des chaînes ; aucune soustraction d'instants.
- **Supprimer un arbre ne supprime pas ses sous-collections.** Firestore n'a pas
  de suppression récursive côté client : il faut vider `personnes`, `unions` et
  `sources` par lots avant de supprimer le document de l'arbre, sinon les données
  restent, orphelines et facturées.
- **Chaque lecture coûte un `get()` de règle en plus.** Lire une personne fait
  lire le document de l'arbre pour connaître le rôle. Firestore met ce `get()` en
  cache à l'intérieur d'une même requête, donc charger 148 personnes ne coûte pas
  148 lectures supplémentaires — mais 148 lectures isolées, si.
- **Les règles ne détectent pas un cycle de filiation.** Rien n'empêche quelqu'un
  de devenir son propre aïeul par une fausse manip. La vérification se fait côté
  client, avant écriture, en parcourant l'ascendance déjà en mémoire.
- **Toute lecture sans `try/catch` laisse « Chargement… » à l'infini** si
  Firestore refuse : contrairement à un appel HTTP, un refus de règle ne fait
  aucun bruit.
- **`serverTimestamps: 'estimate'`** dès qu'on relit un document tout juste
  écrit, sinon le champ vaut `null` et le document semble ne pas exister.

## 7. Prochaines étapes

1. Retravailler la vue de l'arbre — chantier design n° 1, indépendant du reste.
2. ~~Créer le projet Firebase, activer Google, déployer règles et index~~ — fait
   le 5 septembre 2026 (`filiation-vasseur`, voir `REPRISE.md`).
3. Écrire `index.html` : amorçage Firebase, connexion, chargement de l'arbre.
4. Le canevas de l'arbre : calcul des générations, tracé SVG, pan/zoom tactile.
5. Fiche, édition, rattachement, sources.
6. Membres & partage — quand il y aura quelqu'un à inviter.
7. Import GEDCOM (le format d'échange de toute la généalogie) — non commencé,
   c'est ce qui permettra de récupérer un arbre existant depuis Geneanet.

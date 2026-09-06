# Filiation — documentation technique

App d'arbre généalogique **collaboratif**, avec sources d'archives rattachées
aux événements. PWA statique servie par GitHub Pages, qui parle directement à
Firestore depuis le navigateur. Pas de serveur applicatif, pas de Cloud
Function : toute la sécurité tient dans `firestore.rules`.

État au 5 septembre 2026 : **`index.html` est écrit et fonctionne.** Reste à
activer GitHub Pages et à saisir les premières personnes. Voir `REPRISE.md`.

**Un seul arbre pour le moment** : l'app s'ouvre directement sur la vue de
l'arbre, son identifiant étant la constante `ARBRE_ID` (`principal`) en tête
d'`index.html`. Le modèle ci-dessous reste multi-arbres — il ne coûte rien de
plus et évite une migration.

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
assumée, à surveiller au-delà de ~2 000 personnes (voir § 7).

## 3. Modèle de données

Tout vit sous l'arbre : le contrôle d'accès se lit alors en **un seul `get()`**
sur le document de l'arbre, quelle que soit la profondeur.

### `arbres/{arbreId}`

**Les noms cités en exemple dans ce fichier, dans `DESIGN-LIGNEE.md` et dans les
maquettes `design/*.dc.html` sont inventés** — Vasseur, Prigent, Chauvet, Saumur.
Ils ne désignent personne et ne correspondent à aucune donnée de l'arbre. Le
dépôt est public : aucune donnée familiale n'y entre, elles vivent dans
Firestore. Ne pas les remplacer par de vrais noms pour « faire plus réaliste ».

| Champ | Type | Rôle |
|---|---|---|
| `nom` | string | « Famille Vasseur — Prigent » *(inventé)* |
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
| `naissance`, `deces`, `inhumation` | map | `{ date, date_texte, lieu, sources: [sourceId] }` |
| `parents` | array\<personneId\> | 0 à 2 entrées — c'est **l'enfant** qui porte le lien |
| `profession`, `notes` | string | |
| `ref_import` | string | provenance, ex. `505A-p1-s8` — absent d'une saisie à la main |
| `cree_par`, `cree_le`, `maj_par`, `maj_le` | | |

`date` est une chaîne `AAAA-MM-JJ`, jamais un `Timestamp` : une date d'état
civil est une date seule, pas un instant (voir § 7). `date_texte` porte
l'imprécision réelle des archives — « vers 1899 », « avant 1745 », « an VII » —
qui n'entre dans aucun format.

**Trois événements, pas deux.** `inhumation` a été ajoutée le 5 septembre 2026 en
transcrivant le premier tableau d'ascendance de Guillaume : les relevés
généalogiques portent le lieu de sépulture (« Argenteuil, cimetière de Calais »)
au même titre que la naissance et le décès, et c'est une information qui a sa
propre source — un registre de cimetière n'est pas l'acte de décès. La ranger
dans `notes` aurait fait d'un événement sourçable une ligne de texte libre.
Elle a exactement la même forme que les deux autres, elle est donc gratuite
partout : mêmes règles, même bloc d'édition, même rattachement de source.

Le lien de filiation est porté par l'enfant, dans `parents`. Remonter une
ascendance est alors un simple parcours ; la descendance se calcule par index
inverse en mémoire, au chargement.

### `arbres/{arbreId}/unions/{unionId}`

`conjoints: [personneId, personneId]`, `mariage: { date, date_texte, lieu,
sources: [] }`, `divorce` (même forme ou `null`). Une union n'est pas la liste
des enfants : les enfants pointent leurs parents eux-mêmes, l'union ne sert
qu'à porter l'**événement** mariage et ses sources.

L'union porte aussi un `notes` : c'est là qu'un import écrit « Non mariés, selon
le tableau », faute de pouvoir le dire autrement.

`mariage: null` sur une union qui existe quand même veut dire **« non mariés »**,
et c'est une affirmation, pas un trou : les tableaux d'ascendance l'écrivent noir
sur blanc pour les couples qui ont eu des enfants sans passer devant l'état civil.
L'écran doit donc l'afficher tel quel, jamais « mariage inconnu » — ce serait
inventer une lacune là où il y a un fait.

### `arbres/{arbreId}/sources/{sourceId}`

`titre`, `type` (`etat-civil` \| `paroissial` \| `recensement` \| `en-ligne` \|
`autre`), `cote` (« AD 49, 5 Mi 1234, vue 41 — acte n° 112 »), `url`, `notes`.

**La source est rattachée à l'événement, pas à la personne.** C'est l'acte n° 112
qui atteste la naissance du 14 mars 1929 — pas Marcel Vasseur en général. Le
rattachement vit donc dans `naissance.sources`, `deces.sources`,
`inhumation.sources`, `mariage.sources` : un tableau d'identifiants. Le compte inverse (« rattachée à
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
3. **Lignée** — un parchemin qui défile, pan et zoom, bascule Ascendants /
   Descendants, pivot sur n'importe qui. Pas de cartouche : chaque personne est
   écrite dans le support, et la main qui écrit dit le siècle. Le design vient
   de la maquette « Vue Arbre » ; **tout est spécifié dans `DESIGN-LIGNEE.md`,
   à ouvrir avant d'y toucher.**
4. **Fiche d'une personne** — onglets Fiche / Famille / Sources.
5. **Édition** — formulaire ; les blocs Décès et Inhumation n'existent que si
   la personne est décédée.
6. **Rattacher** — on choisit d'abord le lien (père, mère, conjoint, enfant,
   fratrie), puis la personne : existante ou créée dans la foulée.
7. **Membres & partage** — invitation par e-mail, changement de rôle. *Dessiné,
   pas construit : il n'y a encore personne à inviter, et l'onglet n'existe donc
   pas dans la barre de navigation.*
8. **Sources** — liste filtrable par type d'acte.
9. **Import** — atteignable par le menu ⋯ de la vue de l'arbre. Voir § 6.

## 6. L'import d'un tableau d'ascendance

Les documents de départ sont des **tableaux d'ascendance en numérotation Sosa**,
et le format d'import suit le document papier plutôt que le modèle Firestore —
c'est le document qu'on recopie. Une ligne par personne, précédée de son numéro.

```
PAGE   | 505A-p1
SOURCE | titre | type | cote
P      | sosa | nom | prénoms | sexe | profession
         | naiss_date | naiss_lieu | déces_date | déces_lieu | inhum_date | inhum_lieu
X      | sosa pair | date | lieu     ← mariage du couple (sosa, sosa+1)
X      | sosa pair | non marié       ← l'absence attestée, pas l'ignorance
C      | sosa | nom | prénoms | sexe | date | lieu   ← conjoint hors ascendance
ALIAS  | sosa | ref d'une personne déjà importée     ← raccord entre pages
```

**La numérotation Sosa dit à elle seule toute la parenté** : le père de `n` porte
le numéro `2n`, la mère `2n+1`. Les liens et les unions ne se saisissent donc
pas, ils se déduisent — c'est ce qui rend le collage court, et ce qui interdit
qu'un lien contredise un numéro.

Une date qui n'est pas au format `AAAA-MM-JJ` part telle quelle dans
`date_texte` : « vers 1899 » se recopie, il ne se convertit pas.

Tous les événements d'un collage citent la source déclarée en tête. Un tableau
est une source secondaire, `type: 'autre'` — pas un acte. Les actes viendront
par-dessus, avec leurs cotes.

`ref_import` (`505A-p1-s8`) rend l'import **rejouable** : réimporter la même page
met à jour au lieu de dupliquer. C'est aussi ce qui raccorde la page 2 à la
page 1, la même personne y portant deux numéros Sosa différents —
`ALIAS | 1 | 505A-p1-s8` dit que le Sosa 1 de la nouvelle page est déjà là.

**Rien n'est écrit tant qu'une seule ligne est refusée.** Un import à moitié fait
laisserait un arbre à moitié faux, et il n'y a pas d'annulation.

## 7. Pièges — à lire avant de reprendre

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
- **Un `ALIAS` ne raccordait pas ce qu'il raccorde.** La parenté se déduit de la
  numérotation en parcourant les lignes `P` : une personne arrivée par `ALIAS`
  n'en fait pas partie, elle ne recevait donc jamais les parents que la page
  apporte. La page 2 s'importait entière et détachée — seize ancêtres flottant
  au-dessus de la personne dont ils descendent, et rien à l'écran pour le dire,
  puisque chaque page prise séparément semblait juste. C'est réparé
  (`plan.rattachements`) : les parents d'une personne aliassée s'**ajoutent** aux
  siens au lieu de les remplacer, la page qui l'a créée restant seule maîtresse
  du reste de sa fiche.
- **Les règles ne détectent pas un cycle de filiation.** Rien n'empêche quelqu'un
  de devenir son propre aïeul par une fausse manip. La vérification se fait côté
  client, avant écriture, en parcourant l'ascendance déjà en mémoire.
- **Lire un document qui n'existe pas est REFUSÉ, pas vide.** La règle `read` de
  l'arbre fait `uid() in resource.data.membres` ; sur un document absent,
  `resource` vaut `null`, l'évaluation échoue et le SDK rend `permission-denied`.
  Au premier lancement, `getDoc` sur l'arbre lève donc au lieu de rendre un
  snapshot avec `exists() === false` — et le code qui attendait ce `false` pour
  créer l'arbre n'y arrivait jamais : l'app se refusait l'accès à elle-même, en
  accusant le compte. Un refus de lecture au démarrage ne veut pas dire « pas
  membre », il veut dire « pas encore d'arbre » : le seul moyen de faire la
  différence est d'essayer de le créer, et de regarder si *ça* est refusé.
- **Toute lecture sans `try/catch` laisse « Chargement… » à l'infini** si
  Firestore refuse : contrairement à un appel HTTP, un refus de règle ne fait
  aucun bruit.
- **`serverTimestamps: 'estimate'`** dès qu'on relit un document tout juste
  écrit, sinon le champ vaut `null` et le document semble ne pas exister.
- **`setPointerCapture` détourne le `click`.** Le pan du canevas capture le
  pointeur pour survivre à un doigt sorti de la zone ; du coup l'événement
  `click` part sur le canevas et jamais sur le cartouche, qui n'était donc
  jamais sélectionnable. La sélection se fait dans `pointerup`, à partir de la
  cible mémorisée au `pointerdown`.
- **L'attribut `hidden` perd contre une règle CSS.** `#tiroir { display: flex }`
  l'emporte sur le `display: none` que le navigateur attache à `[hidden]` : le
  tiroir de sélection restait ouvert en permanence, vide. Il faut une règle
  `#tiroir[hidden] { display: none }` explicite.
- **Un bandeau d'information capte les clics.** `#alerte` recouvrait pendant six
  secondes ce qui passait sous lui — le bouton « Ajouter une personne » d'un
  arbre vide, les entrées du bas d'une feuille modale — et les rendait
  intouchables sans que rien ne l'explique. `pointer-events: none` : un message
  ne se clique pas.
- **`flex: 1 1 0` écrase au lieu de faire défiler.** La classe `.defile`,
  appliquée au corps d'une feuille modale, comprimait ses enfants : un bouton de
  56 px n'en faisait plus que 24 et débordait sous le bas de l'écran, donc
  restait intouchable. Dans une feuille, le corps prend `flex: 0 1 auto` et ses
  enfants `flex: 0 0 auto`.
- **Quatre générations ne tiennent pas dans 390 px.** Huit arrière-grands-parents
  côte à côte dépassent 1 300 px : les faire tenir dans la largeur d'un téléphone
  réduit les noms à quatre pixels. La vue Lignée l'assume — le parchemin déborde
  et l'on déroule — mais elle resserre chaque rangée autour du centre, sans quoi
  la largeur imposée par la rangée la plus peuplée écarte les deux parents de la
  souche hors de l'écran. Voir `DESIGN-LIGNEE.md` § 11.

## 8. Prochaines étapes

1. ~~Créer le projet Firebase, activer Google, déployer règles et index~~ — fait
   le 5 septembre 2026 (`filiation-vasseur`, voir `REPRISE.md`).
2. ~~Écrire `index.html` : amorçage Firebase, connexion, chargement de l'arbre~~
   — fait le 5 septembre 2026.
3. ~~Le canevas de l'arbre : calcul des générations, tracé SVG, pan/zoom
   tactile~~ — fait le 5 septembre 2026.
4. ~~Fiche, édition, rattachement, sources~~ — fait le 5 septembre 2026.
5. Activer GitHub Pages, et ajouter le domaine dans les domaines autorisés de
   Firebase Authentication.
6. Retravailler la vue de l'arbre — chantier design n° 1, indépendant du reste.
7. Membres & partage — quand il y aura quelqu'un à inviter.
8. Import GEDCOM (le format d'échange de toute la généalogie) — non commencé,
   c'est ce qui permettra de récupérer un arbre existant depuis Geneanet.

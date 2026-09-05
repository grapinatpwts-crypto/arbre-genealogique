# DESIGN — Vue « Lignée » (parchemin)

Spécification de la vue arbre/lignée. Source de vérité : `Vue Arbre.dc.html`
(projet de design). À placer à la racine du dépôt, à côté de `REPRISE.md`.

## 1. Parti pris

Un **parchemin unique** défilant verticalement. Pas d'arbre dessiné, pas de
cartouche, pas d'encadré : chaque personne est **écrite dans le support**, comme
une mention d'acte. Trois signaux disent l'ancienneté d'une ligne :

1. l'usure du parchemin (teinte, taches, piqûres) qui croît vers le haut ;
2. la police et la main qui changent par tranche de siècle ;
3. l'encre qui s'assombrit et bave, les traits de plume qui s'affinent.

La rangée la plus récente est **en bas** en ascendance ; on remonte le temps en
remontant la feuille. En descendance, l'ordre s'inverse (le point de départ en
haut) mais l'enfant reste toujours la rangée du dessous.

## 2. Palette

| Rôle | Valeur |
|---|---|
| Parchemin | `#EBDFC2` |
| Fond hors feuille | `#DACBA8` |
| Taches / brûlure | bruns `rgba(112,74,34,…)` → `rgba(96,62,26,…)` |
| Encre présent → XVIᵉ | `#2C2317` · `#33291C` · `#33261A` · `#2B2014` · `#291E12` · `#241A0F` |
| Traits de plume | `#241A0F` |
| Repère de siècle | `#6B4522` |
| Accent d'interaction | `#9A5233` |
| Bleu d'archive (source) | `#3D5A8C` |
| Interface hors canevas | `#F3EDE1`, `#FBF7EF`, bordures `#C9BCA6`, `#DCD2C0` |
| Textes d'interface | `#1F1A14`, `#4A4137`, `#6E6357`, `#8A7D6D`, `#9C8F7D` |

## 3. Typographie par époque — table `ERES`

Une clé par tranche. **Aucune police distante** : l'appel Google Fonts échouait
et rendait toutes les époques identiques. Uniquement des piles système.

| Clé | Tranche | Police | Style | Approche | Encre |
|---|---|---|---|---|---|
| `contemporain` | XXIᵉ | Calibri, Segoe UI, system-ui | droit | 0.005em | `#2C2317` |
| `moderne` | XXᵉ | Calibri, Segoe UI, system-ui | droit | 0.03em | `#33291C` |
| `belleEpoque` | XIXᵉ | Times New Roman | petites capitales | 0.1em | `#33261A` |
| `empire` | déb. XIXᵉ | Times New Roman | italique | 0.12em | `#2B2014` |
| `ancienRegime` | XVIIᵉ | pile `PLUME` | italique + `skewX(-13deg)` | 0.02em | `#291E12` |
| `renaissance` | XVIᵉ | pile `PLUME` | italique + `skewX(-17deg)` | 0.04em | `#241A0F` |

Règle : **Calibri après 1900 · Times New Roman avant 1900 · anglaise avant 1700.**

```
PLUME = 'Tangerine', 'Great Vibes', 'Snell Roundhand', 'Apple Chancery',
        'Monotype Corsiva', 'Lucida Calligraphy', 'Lucida Handwriting',
        'Segoe Script', 'Ink Free', 'Brush Script MT', cursive
```

L'inclinaison à la plume (`skewX`) est indispensable : elle porte l'effet
manuscrit sur les machines où aucune anglaise n'est installée. Pas de petites
capitales avant 1700 — elles contredisent la main courante.

Chaque ère porte aussi : `bavure` (text-shadow, croissant avec l'âge),
`chiffres` (`tabular-nums` seulement après 1900), `nomSiecle` (repère en marge)
et `epoque` (mention affichée dans la feuille de sélection).

## 4. Métrique — `corps(ere)`

**Règle absolue : aucun décalage vertical en dur.** Tous se déduisent du bloc de
texte, dont la hauteur varie selon l'époque.

```js
function corps(ere) {
  const vieux = ere === 'renaissance' || ere === 'ancienRegime' || ere === 'empire';
  const taille = ere === 'renaissance' ? 26 : ere === 'ancienRegime' ? 24
               : ere === 'empire' ? 22 : 19;
  const tailleDate = vieux ? 17 : 13.5;
  const tailleLieu = vieux ? 15 : 12;
  const lh   = Math.ceil(taille * 1.14);   // interligne ENTIER
  const hNom = lh * 2;                      // deux lignes de nom TOUJOURS réservées
  const h    = hNom + 2 + 3 + tailleDate * 1.3 + 3 + tailleLieu * 1.3;
  return { taille, tailleDate, tailleLieu, lh, hNom, demi: h / 2 };
}
```

Le nom est rendu dans une boîte de hauteur fixe `hNom`, texte centré,
`line-height: lh px`. Hauteur calculée et hauteur rendue coïncident donc
exactement, avec ou sans retour à la ligne.

Décalages dérivés :

| Élément | Position |
|---|---|
| Swash d'alliance | `y + demi + 14` |
| Départ de filiation (parent) | `y + demi + 20` |
| Arrivée de filiation (enfant) | `y_enfant − demi(enfant) − 14` |
| Repère de siècle | `y − demi − 34` |

Deux régressions viennent de là : interligne fractionnaire (seconde ligne
tranchée) et constantes en dur (traits traversant les noms). Ne pas y revenir.

## 5. Traits de plume

Jamais de connecteur orthogonal, jamais de `stroke` d'épaisseur constante.
Chaque lien est un **chemin rempli** : deux courbes en S refermées, fine côté
ancêtre (`w0 = 1.6`), épaisse côté descendant (`w1 = 5.4`).

```js
function plume(x0, y0, x1, y1, w0, w1, dev) {
  const k = (y1 - y0) * 0.62;
  const a = x0 + dev, b = x1 - dev;
  return `M ${x0-w0/2} ${y0} C ${a-w0/2} ${y0+k} ${b-w1/2} ${y1-k} ${x1-w1/2} ${y1}`
       + ` L ${x1+w1/2} ${y1} C ${b+w1/2} ${y1-k} ${a+w0/2} ${y0+k} ${x0+w0/2} ${y0} Z`;
}
```

`dev = signe(dx) × (16 + min(26, |dx| × 0.18))` — un dévers latéral existe même
sur un lien vertical, sinon le S disparaît.

**Alliance** : swash rempli sous le couple, deux courbes légèrement décalées
entre les deux noms, opacité `0.72 − age × 0.18`. Pas de barre droite.

Opacité et finesse décroissent avec l'âge : filiation `0.86 − age × 0.16`, où
`age = indice / (total − 1)`, 0 pour la rangée la plus récente, 1 pour la plus
ancienne.

## 6. Vieillissement du support

Cumulé sur le bloc parchemin, du plus récent (bas) au plus ancien (haut) :

- **Teinte** : `linear-gradient(to top, transparent 34%, rgba(120,84,42,.16) 62%, rgba(104,70,34,.34) 86%, rgba(88,58,28,.5) 100%)`.
- **Grain** : `repeating-linear-gradient` 1 px / 5 px, `rgba(140,106,60,.05)`.
- **Taches et piqûres** : calque `mix-blend-mode: multiply`, opacité 0.62,
  dix `radial-gradient` de tailles décroissantes — denses en haut (6 %–30 %),
  rares en bas (46 %–58 %).
- **Brûlure d'encadrement** : `box-shadow: inset 0 0 34px rgba(96,60,24,.55), inset 0 0 90px rgba(112,74,34,.28)`.
- **Bord déchiqueté** : `clip-path: polygon(...)` généré par `dechirure(largeur, hauteur)`
  (PRNG à graine fixe `4711`, amplitude `5 + 13 × (1 − y/h)` — plus mordu en haut).
- **Bandeau supérieur** : dégradé brun `multiply` sur 110 px, le haut de la
  feuille se perd dans l'ombre.

Le prop `usure` (booléen, défaut `true`) neutralise la dégradation typographique
et d'opacité pour comparer les époques à support égal.

## 7. Layout et navigation

```
LARGE = 560   // largeur du parchemin (px canevas)
PAS   = 168   // pas vertical entre deux générations
MARGE = 96    // marge haute et basse
ECH   = 0.7   // échelle d'ouverture
```

- Une **rangée par génération**, personnes réparties régulièrement sur `LARGE`
  (`pas = LARGE / n`, centre à `pas × (j + 0.5)`). Largeur de mention :
  205 px (≤ 2 personnes), 165 px (3), 128 px (4+).
- Hauteur totale : `MARGE × 2 + (rangées − 1) × PAS`.
- **Cadrage d'ouverture** : `ty = 286 − hauteur × ECH` — 286 = bas de la fenêtre
  de canevas moins la feuille de sélection, pour que la rangée la plus récente
  reste visible au chargement.
- Pan à la souris et au doigt, molette pour zoomer, échelle bornée `0.3 – 1.3`.
  « Viser » recadre la sélection à l'échelle 1.
- Une rangée peut être une **lacune** : `{ lacune: 'texte' }` rend une mention
  italique centrée (`· · · texte · · ·`) au lieu de personnes — matérialise une
  génération non documentée (registres détruits, etc.).

## 8. Données attendues

```js
// Une entrée par génération, de la plus récente à la plus ancienne (ASC).
{ ere: 'moderne', gens: [
  { id: 'marcel', nom: 'Marcel Vasseur', dates: '1929 – 2011',
    lieu: 'Saumur (49)', src: 3, enfants: ['etienne'], epouse: 'suzanne' }
]}
{ lacune: 'cinq générations non retrouvées — registres détruits en 1793' }
```

- `src` : nombre d'actes rattachés. `0` ⇒ carré vide et mention « Aucune source —
  information non attestée » ; `> 0` ⇒ carré `#3D5A8C`.
- `enfants` : ids de la rangée du dessous. Plusieurs parents pointant le même
  enfant sont regroupés : le trait part du milieu du couple.
- `epouse` : id du conjoint dans la **même** rangée ; déclenche le swash.

En descendance, `enfants` est posé dans l'autre sens (parent en haut).

## 9. Props exposés

| Prop | Éditeur | Défaut | Effet |
|---|---|---|---|
| `vueInitiale` | enum `asc`/`desc` | `asc` | sens d'ouverture |
| `accent` | color | `#9A5233` | soulignement de sélection, onglet actif, bouton primaire |
| `usure` | boolean | `true` | vieillissement typographique et d'opacité |

## 10. Interdits

- Toute police chargée à distance.
- Une feuille de style à classes (tout est en styles en ligne).
- Un décalage vertical constant au lieu de `corps(ere)`.
- Un connecteur orthogonal ou un trait d'épaisseur constante.
- Un cadre, une carte ou un fond derrière un nom.

## 11. Écarts de l'app par rapport à la maquette

La maquette travaille sur des données écrites à la main, choisies pour tenir.
`index.html` travaille sur ce que contient l'arbre. Cinq écarts en découlent ;
ils sont volontaires, et c'est ici qu'il faut les rediscuter — pas dans le code.

**L'ère se déduit de l'année, pas du rang de la rangée.** La maquette attache
l'ère à la génération. Dans l'app les dates sont réelles : une génération peut
chevaucher deux siècles, et c'est le document qui a raison. Bornes retenues :
`≥ 1950` contemporain · `1900` moderne · `1830` belleEpoque · `1700` empire ·
`1600` ancienRegime · avant renaissance. L'ère d'une rangée est celle de sa
personne **la plus ancienne** — dans un couple à cheval sur 1900, c'est l'aînée
qui donne le ton du support.

**Les rangées se resserrent autour du centre.** `pas = LARGE / n` étale une
rangée sur toute la feuille ; avec huit arrière-grands-parents, les deux parents
de la souche se retrouvaient à six cents pixels l'un de l'autre, hors écran,
alors qu'ils sont ce qu'on regarde en premier. L'app pose
`pas = min(LARGE / n, 246)` et centre la rangée.

**La feuille s'élargit au-delà de quatre par rangée** : `LARGE = max(560, n × 150)`.
Huit noms lisibles n'entrent pas dans 390 px — c'est arithmétique. Plutôt
qu'écrire trop petit pour être lu, le parchemin déborde et l'on déroule
latéralement. Le cadrage d'ouverture reste centré sur la souche.

**Le repère de siècle s'aligne sur sa rangée**, au lieu des 14 px du bord gauche
de la feuille : sur un parchemin large, un repère collé au bord n'est jamais
dans le champ.

**Le cadrage réserve la place de la feuille de sélection** (marge de 200 px),
ouverte ou non — sinon toucher la souche la fait disparaître sous le tiroir
qu'on vient d'ouvrir sur elle. La maquette codait 286 en dur ; l'app le calcule
sur la hauteur réelle du canevas, qui varie avec l'appareil.

**Les lacunes ne sont pas générées.** Le rendu existe (§ 7), mais aucune lacune
n'apparaît : le modèle de données ne porte pas encore l'information, et une
génération manquante ne se devine pas d'un trou dans l'ascendance — « registres
détruits en 1793 » est une affirmation, qui demande une source. À reprendre
quand le modèle saura la porter.

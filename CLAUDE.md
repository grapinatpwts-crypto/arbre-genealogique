# Filiation — fiche de reprise

App d'arbre généalogique collaboratif, avec les sources d'archives rattachées
aux événements. PWA statique servie par GitHub Pages, qui parle directement à
Firestore depuis le navigateur. **Pas de serveur applicatif, pas de Cloud
Function** : toute la sécurité tient dans `firestore.rules`. Plan Spark, coût
nul par utilisateur — c'est la contrainte qui a dicté l'architecture, reprise
telle quelle de `coaching-musculation`.

**État : l'app est écrite et en ligne. Reste à saisir les documents.**
Reprendre par `REPRISE.md`, qui dit où on en est et par quoi continuer.

## Où lire quoi

| Question | Fichier |
|---|---|
| Où on en est, quoi faire ensuite | `REPRISE.md` |
| Comment l'app fonctionne (données, écrans, pièges) | `PROJET.md` |
| Comment on l'installe de zéro | `README.md` |
| À quoi ça ressemble | `design/*.dc.html`, et le canevas Claude Design |

`PROJET.md` § 6 (« Pièges ») et § 7 (« Prochaines étapes ») sont les deux
sections à ouvrir en premier pour reprendre le travail.

## Comment on travaille ici

- **Tout s'écrit en français** : réponses, commits, documentation, commentaires.
- Un commentaire dit **pourquoi**, souvent en racontant ce qui n'a pas marché
  avant. Jamais une paraphrase du code.
- **Direct sur `main`**, sans branche. Chaque changement livré porte, dans le
  même commit : la doc mise à jour quand le comportement décrit change, et
  `CACHE` incrémenté dans `sw.js` — sinon la PWA garde l'ancienne coquille.
- **`git push` après chaque commit**, sans attendre qu'on le demande.
- `index.html` sera un monolithe (HTML + CSS + JS inline). Vérifier la syntaxe
  avant de committer : extraire chaque bloc `<script>` et `node --check`.
- **Vérifier ce qui se voit avant de livrer.** Une page servie en local
  (`python3 -m http.server`) suffit pour une icône ; pour une fonction, extraire
  son vrai code d'`index.html` et l'exécuter sur quelques cas vaut mieux que de
  le relire.

## Le piège qui coûte le plus cher

**Un `git push` ne déploie pas `firestore.rules`.** Les règles demandent

```bash
firebase deploy --only firestore:rules
```

Un correctif de règles resté non déployé donne l'illusion que le bug est corrigé
alors que le refus serveur persiste. Le signaler dès que le fichier change, ne
jamais le supposer fait.

## Un seul arbre, pour le moment

Décidé le 4 septembre 2026 : il n'y aura **qu'un seul arbre**. L'app s'ouvre
directement dessus, l'écran « Mes arbres » est dessiné mais pas construit, et
l'identifiant de l'arbre est une constante en tête d'`index.html`. Le modèle de
données garde quand même `arbres/{arbreId}` et ses sous-collections : ça ne
coûte rien aujourd'hui et ça évite une migration le jour où il y en aura
plusieurs.

## Le principe qu'on ne rediscute pas sans décision explicite

**Une information sans source reste une information sans source.** L'app ne
comble jamais un trou toute seule : pas de date déduite, pas de lieu supposé,
pas de rapprochement automatique entre deux homonymes. Elle affiche ce qui est
saisi, et ce qui l'atteste. C'est ce qui la sépare d'un arbre de complaisance.

## Le design

Les maquettes viennent de Claude Design : `design/*.dc.html` (un fichier par
écran) plus `design/canvas.json` pour la mise en page du canevas. Pour les
modifier, on édite ces fichiers et on **re-sème** le canevas — jamais le
`filiation.html` produit, qui est régénéré et ignoré par git.

Charte : papier d'archive. Fond crème `#F3EDE1`, cartes `#FBF7EF`, encre
`#1F1A14`, filets `#DCD2C0`, accent sanguine `#9A5233`, bleu d'archive `#3D5A8C`
pour tout ce qui touche aux sources. **EB Garamond** pour les noms et les
titres, **Archivo** pour l'interface. Angles à 4 px, pas plus : c'est un
registre, pas une application de messagerie.

## Coordonnées

- Dépôt : `grapinatpwts-crypto/arbre-genealogique` (public — GitHub Pages ne
  sert pas les dépôts privés sur le plan gratuit ; le dépôt ne contient aucune
  donnée familiale, elles vivent dans Firestore)
- En ligne : https://grapinatpwts-crypto.github.io/arbre-genealogique/
- Firebase : projet `filiation-vasseur`, Firestore en `europe-west9` (Paris),
  Auth Google activée. Config de l'appli web « Arbre généalogique » dans
  `REPRISE.md` (à recopier dans `index.html` une fois écrit).
- Seul vrai secret du projet : `scripts/service-account.json` (ignoré par git).
  La config Firebase visible dans `index.html` est publique par nature.

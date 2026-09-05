#!/usr/bin/env python3
"""Génère les trois icônes de la PWA depuis le glyphe de l'écran de connexion.

    pip install Pillow && python3 scripts/icones.py

À relancer seulement si le glyphe ou la charte changent : les PNG produits sont
commités, l'app ne dépend pas de ce script à l'exécution. Sans eux, `addAll`
dans `sw.js` échoue et le service worker ne s'installe jamais.
"""
from PIL import Image, ImageDraw

CREME = (243, 237, 225)     # --creme
SANGUINE = (154, 82, 51)    # --sanguine


def dessiner(taille, marge_rel):
    """Une souche pleine, deux branches, deux aïeux creux.

    Le dessin se fait 8× trop grand puis se réduit : c'est ce qui donne des
    bords lisses sans avoir à gérer l'anticrénelage à la main.

    `marge_rel` est la marge de sécurité. Une icône maskable en réclame bien
    plus : le système y découpe un cercle, et tout ce qui touche le bord y passe.
    """
    S = taille * 8
    img = Image.new('RGB', (S, S), CREME)
    d = ImageDraw.Draw(img)

    # Le glyphe tient dans une grille de 30 × 34, centrée sur l'icône.
    u = S * (1 - 2 * marge_rel) / 34.0
    ox, oy = S / 2 - 15 * u, S / 2 - 17 * u
    X = lambda x: ox + x * u
    Y = lambda y: oy + y * u
    trait = max(2, round(1.5 * u))
    r = 3.2 * u

    # Les branches s'arrêtent AU BORD des cercles, pas à leur centre : sinon le
    # trait traverse l'anneau creux et y laisse une encoche bien visible.
    bord = Y(7) + r
    # Un seul polyline par branche : PIL raccorde alors les angles proprement,
    # là où des segments séparés laissaient dépasser leurs extrémités carrées.
    d.line([X(15), Y(28) - r, X(15), Y(19), X(3), Y(19), X(3), bord],
           fill=SANGUINE, width=trait, joint='curve')
    d.line([X(15), Y(19), X(27), Y(19), X(27), bord],
           fill=SANGUINE, width=trait, joint='curve')

    d.ellipse([X(15) - r, Y(28) - r, X(15) + r, Y(28) + r], fill=SANGUINE)
    for cx in (3, 27):
        d.ellipse([X(cx) - r, Y(7) - r, X(cx) + r, Y(7) + r],
                  outline=SANGUINE, width=trait)

    return img.resize((taille, taille), Image.LANCZOS)


if __name__ == '__main__':
    dessiner(192, 0.17).save('icon-192.png')
    dessiner(512, 0.17).save('icon-512.png')
    dessiner(512, 0.28).save('icon-512-maskable.png')
    print('icon-192.png, icon-512.png, icon-512-maskable.png')

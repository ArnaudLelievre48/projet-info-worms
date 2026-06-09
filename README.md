# Projet info - Worms

Jeu inspire de Worms, developpe en Python avec Pygame. Deux joueurs s'affrontent sur une carte destructible : ils placent des wormz, achetent des armes, tirent des missiles ou des strikes, et utilisent la physique du terrain pour faire tomber ou detruire les adversaires.

## Fonctionnalites

- Affichage temps reel avec Pygame.
- Terrain genere depuis des images dans `map/`.
- Textures de terrain, wormz et armes dans `textures/`.
- Physique de sable et de gravite pour les wormz.
- Missiles avec trajectoire courbe et strikes verticaux.
- Terrain destructible ou transformable en sable apres explosion.
- Sauvegarde et chargement des parties avec SQLite (`game.db`).
- Configuration personnalisable via un fichier DSL.
- Tests unitaires pour la physique, les armes, les formes et les wormz.

## Installation

Ce projet utilise Python 3 et les bibliotheques suivantes :

- `pygame`
- `numpy`
- `matplotlib`

Installation des dependances :

```bash
python3 -m pip install pygame numpy matplotlib
```

## Lancement

Pour demarrer le jeu :

```bash
python3 main.py
```

Au lancement, le menu permet de commencer une nouvelle partie ou de charger une sauvegarde existante. Les sauvegardes disponibles sont listees dans le terminal.

## Configuration personnalisee

Il est possible de lancer une partie avec un fichier de configuration :

```bash
python3 main.py -c config.conf
```

Exemple de syntaxe :

```conf
player 1 money 1500
player 2 money 500
player 1 worm 25 48 health=3 range=120 weight=5
player 1 missiles 3
player 1 strikes 1
price worm 200
price missile 150
price strike 300
bonus kill_reward 150
weapon missile damage=3 radius_range=100 radius_explosion=5 radius_break=8
```

Les lignes vides et les commentaires commencant par `#` sont ignores.

## Commandes

| Commande | Action |
| --- | --- |
| Clic gauche | Acheter et placer un worm |
| Clic droit | Lancer l'arme selectionnee |
| `Tab` | Changer le worm utilise pour tirer |
| `Maj gauche` | Changer le type d'arme |
| `Entree` | Terminer le tour |
| `M` | Acheter un missile |
| `S` | Acheter un strike |
| `R` | Rafraichir la fenetre |
| `Q` | Sauvegarder et quitter |
| `N` | Changer la sauvegarde selectionnee dans le menu |

Chaque joueur dispose de 3 actions par tour. Acheter un worm ou un missile coute 1 action ; acheter un strike coute 2 actions.

## Sauvegardes

Les sauvegardes sont stockees dans `game.db`.

Quand le joueur appuie sur `Q`, l'etat courant est sauvegarde :

- grille du terrain ;
- argent des joueurs ;
- positions, points de vie et statistiques des wormz ;
- inventaire et statistiques des armes.

Au prochain lancement, le menu permet de charger une sauvegarde existante.

## Tests

Pour lancer les tests unitaires :

```bash
python3 unit_tests.py
```

Pour lancer le benchmark de la physique et generer `step_efficiency.png` :

```bash
python3 unit_tests.py --benchmark
```

## Structure du projet

| Fichier/dossier | Role |
| --- | --- |
| `main.py` | Point d'entree, boucle de jeu, sauvegardes et gestion des entrees |
| `display.py` | Affichage Pygame/Matplotlib, interface et menu |
| `physics.py` | Gravite des wormz et physique du sable |
| `assets.py` | Classes `Player`, `Worm`, `missile` et `strike` |
| `DSL.py` | Chargement des configurations personnalisees |
| `shapes.py` | Formes et transformations du terrain |
| `unit_tests.py` | Tests unitaires et benchmark |
| `map/` | Images utilisees pour construire la carte |
| `textures/` | Textures affichees dans le jeu |
| `game.db` | Base SQLite des sauvegardes |

## Licence

Voir le fichier `LICENSE`.

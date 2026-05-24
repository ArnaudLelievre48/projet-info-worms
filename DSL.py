import copy
import re

import assets


# stats par defaut des armes
DEFAULT_WEAPON_STATS = {
    "missile": {
        "radius_range": 100,
        "radius_explosion": 5,
        "radius_break": 8,
        "damage": 3,
    },
    "strike": {
        "radius_range": 400,
        "radius_explosion": 5,
        "radius_break": 15,
        "damage": 2,
    },
}


# liste des patterns REGEX que l'on essaye d'identifier à chaque ligne
LINE_PATTERNS = {
    "money": re.compile(r"^player\s+([12])\s+money\s+(-?\d+)\s*$", re.I),
    "worm": re.compile(r"^player\s+([12])\s+worm\s+(-?\d+)\s+(-?\d+)(.*)$", re.I),
    "weapon_count": re.compile(r"^player\s+([12])\s+(missiles|strikes)\s+(\d+)\s*$", re.I),
    "price": re.compile(r"^price\s+(worm|missile|strike)\s+(\d+)\s*$", re.I),
    "bonus": re.compile(r"^bonus\s+(kill_reward)\s+(\d+)\s*$", re.I),
    "weapon_stats": re.compile(r"^weapon\s+(missile|strike)(.*)$", re.I),
}

OPTION_PATTERN = re.compile(r"(\w+)\s*=\s*(-?\d+(?:\.\d+)?)")


def default_config(ny=108):
    """
    permet de créer les personnage avec toutes ses propriétés, un peu comme quand on suavegarde une partie et qu'on load une partie
    """
    return {
        "players": [
            {
                "money": 1000,
                "wormz": [{"x": 25, "y": ny - 59 - 1, "health": 3, "worm_range": 120, "weight": 5}],
                "missiles": 3,
                "strikes": 0,
            },
            {
                "money": 1000,
                "wormz": [{"x": 163, "y": ny - 41 - 1, "health": 3, "worm_range": 120, "weight": 5}],
                "missiles": 3,
                "strikes": 0,
            },
        ],
        "prices": {"worm": 200, "missile": 150, "strike": 300},
        "bonuses": {"kill_reward": 150},
        "weapon_stats": copy.deepcopy(DEFAULT_WEAPON_STATS),
    }


def parse_value(raw_value):
    """
    permet de convertir en int ou en float les valeurs lorsq'on lit la config
    """
    value = float(raw_value)
    if value.is_integer():
        return int(value)
    return value


def parse_options(raw_options):
    return {
        key: parse_value(value)
        for key, value in OPTION_PATTERN.findall(raw_options)
    }


def player_config(config, player_number, line_number):
    """
    converti l'index et retourne la config du jour voulu
    """
    # permet de lire player 1 pour player d'indice 0, et player 2 pour player d'indice 1
    index = int(player_number) - 1
    if not 0 <= index < len(config["players"]):
        raise ValueError(f"ligne {line_number}: joueur invalide: {player_number}")
    return config["players"][index]


def apply_weapon_stats(weapon, stats):
    """
    applique à weapon les parametres rentrés en stat
    """
    weapon.radius_range = stats["radius_range"]
    weapon.radius_explosion = stats["radius_explosion"]
    weapon.radius_break = stats["radius_break"]
    weapon.damage = stats["damage"]
    return weapon


def make_weapon(player, weapon_name, stats):
    """
    permet d'instancier un missile ou une strike, puis applique les stats avant de le retourner
    """
    if weapon_name == "missile":
        weapon = player.missile()
    elif weapon_name == "strike":
        weapon = player.strike()
    else:
        raise ValueError(f"arme inconnue: {weapon_name}")

    return apply_weapon_stats(weapon, stats)


def load_config(path, ny=108):
    """
    Charge un fichier de configuration custom dans un dictionnaire simple.

    Syntaxe supportee:
      player 1 money 1500
      player 1 worm 25 48 health=3 range=120 weight=5
      player 1 missiles 3
      player 1 strikes 1
      price worm 200
      price missile 150
      price strike 300
      bonus kill_reward 150
      weapon missile damage=3 radius_range=100 radius_explosion=5 radius_break=8

    Les lignes vides et les commentaires commencant par # sont ignores.
    """

    config = default_config(ny)
    custom_wormz = set()

    with open(path, encoding="utf-8") as config_file:
        for line_number, raw_line in enumerate(config_file, start=1):

            # sépare le contenu des commentiares
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            # match les patterns avec du REGEX et applique les paramètres au Player correspondant

            if match := LINE_PATTERNS["money"].match(line):
                player = player_config(config, match.group(1), line_number)
                player["money"] = int(match.group(2))

            elif match := LINE_PATTERNS["worm"].match(line):
                player_index = int(match.group(1)) - 1
                player = player_config(config, match.group(1), line_number)

                if player_index not in custom_wormz:
                    player["wormz"] = []
                    custom_wormz.add(player_index)

                options = parse_options(match.group(4))
                player["wormz"].append(
                    {
                        "x": int(match.group(2)),
                        "y": int(match.group(3)),
                        "health": options.get("health", 3),
                        "worm_range": options.get("range", options.get("worm_range", 120)),
                        "weight": options.get("weight", 5),
                    }
                )

            elif match := LINE_PATTERNS["weapon_count"].match(line):
                player = player_config(config, match.group(1), line_number)
                player[match.group(2).lower()] = int(match.group(3))

            elif match := LINE_PATTERNS["price"].match(line):
                config["prices"][match.group(1).lower()] = int(match.group(2))

            elif match := LINE_PATTERNS["bonus"].match(line):
                config["bonuses"][match.group(1).lower()] = int(match.group(2))

            elif match := LINE_PATTERNS["weapon_stats"].match(line):
                weapon_name = match.group(1).lower()
                options = parse_options(match.group(2))
                unknown_options = set(options) - set(config["weapon_stats"][weapon_name])
                if unknown_options:
                    unknown = ", ".join(sorted(unknown_options))
                    raise ValueError(
                        f"ligne {line_number}: option d'arme inconnue: {unknown}"
                    )
                config["weapon_stats"][weapon_name].update(options)

            else:
                raise ValueError(f"ligne {line_number}: syntaxe invalide: {raw_line.rstrip()}")

    return config


def create_players(config):
    """
    permet de créer les Players et de charger les wormz et weapons dans l'inventaire du joueur
    """
    players = []

    for player_config_data in config["players"]:
        player = assets.Player(money=player_config_data["money"])

        for worm_id, worm_config in enumerate(player_config_data["wormz"]):
            player.wormz.append(
                player.Worm(
                    worm_config["x"],
                    worm_config["y"],
                    health=worm_config["health"],
                    worm_range=worm_config["worm_range"],
                    weight=worm_config["weight"],
                    worm_id=worm_id,
                )
            )

        for _ in range(player_config_data["missiles"]):
            player.weapons[0].append(
                make_weapon(player, "missile", config["weapon_stats"]["missile"])
            )

        for _ in range(player_config_data["strikes"]):
            player.weapons[1].append(
                make_weapon(player, "strike", config["weapon_stats"]["strike"])
            )

        players.append(player)

    return players

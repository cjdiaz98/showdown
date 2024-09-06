from constants import PokemonType

from typing import Dict
from constants import PokemonType

def create_type_multiplier_dict(
    normal_multiplier: float = 1.0,
    fire_multiplier: float = 1.0,
    water_multiplier: float = 1.0,
    electric_multiplier: float = 1.0,
    grass_multiplier: float = 1.0,
    ice_multiplier: float = 1.0,
    fighting_multiplier: float = 1.0,
    poison_multiplier: float = 1.0,
    ground_multiplier: float = 1.0,
    flying_multiplier: float = 1.0,
    psychic_multiplier: float = 1.0,
    bug_multiplier: float = 1.0,
    rock_multiplier: float = 1.0,
    ghost_multiplier: float = 1.0,
    dragon_multiplier: float = 1.0,
    dark_multiplier: float = 1.0,
    steel_multiplier: float = 1.0,
    fairy_multiplier: float = 1.0
) -> Dict[str, float]:
    """
    Creates a dictionary of type multipliers using PokemonType enums as keys and multipliers as values.
    
    Args:
        Multipliers for each Pokémon type as named arguments, with default value 1.0.

    Returns:
        dict: A dictionary with the PokemonType enum values as keys and multipliers as values.
    """
    return {
        PokemonType.normal.value: normal_multiplier,
        PokemonType.fire.value: fire_multiplier,
        PokemonType.water.value: water_multiplier,
        PokemonType.electric.value: electric_multiplier,
        PokemonType.grass.value: grass_multiplier,
        PokemonType.ice.value: ice_multiplier,
        PokemonType.fighting.value: fighting_multiplier,
        PokemonType.poison.value: poison_multiplier,
        PokemonType.ground.value: ground_multiplier,
        PokemonType.flying.value: flying_multiplier,
        PokemonType.psychic.value: psychic_multiplier,
        PokemonType.bug.value: bug_multiplier,
        PokemonType.rock.value: rock_multiplier,
        PokemonType.ghost.value: ghost_multiplier,
        PokemonType.dragon.value: dragon_multiplier,
        PokemonType.dark.value: dark_multiplier,
        PokemonType.steel.value: steel_multiplier,
        PokemonType.fairy.value: fairy_multiplier,
    }

DEFENDING_TYPE_MATCHUPS = {
	# Key is the defending type. Dictionaries contain attacking type multipliers
    PokemonType.normal.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=2, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=1, ghost_multiplier=0, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.fire.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=0.5, water_multiplier=2, electric_multiplier=1, grass_multiplier=0.5, ice_multiplier=0.5,
        fighting_multiplier=1, poison_multiplier=1, ground_multiplier=2, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=0.5,
        rock_multiplier=2, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=0.5, fairy_multiplier=0.5
    ),

    PokemonType.water.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=0.5, water_multiplier=0.5, electric_multiplier=2, grass_multiplier=2, ice_multiplier=0.5,
        fighting_multiplier=1, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=0.5, fairy_multiplier=1
    ),

    PokemonType.electric.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=0.5, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=1, poison_multiplier=1, ground_multiplier=2, flying_multiplier=0.5, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=0.5, fairy_multiplier=1
    ),

    PokemonType.grass.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=2, water_multiplier=0.5, electric_multiplier=0.5, grass_multiplier=0.5, ice_multiplier=2,
        fighting_multiplier=1, poison_multiplier=2, ground_multiplier=0.5, flying_multiplier=2, psychic_multiplier=1, bug_multiplier=2,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.ice.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=2, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=0.5,
        fighting_multiplier=2, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=2, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=2, fairy_multiplier=1
    ),

    PokemonType.fighting.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=1, poison_multiplier=1, ground_multiplier=1, flying_multiplier=2, psychic_multiplier=2, bug_multiplier=0.5,
        rock_multiplier=0.5, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=.5, steel_multiplier=1, fairy_multiplier=2
    ),

    PokemonType.poison.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=0.5, poison_multiplier=0.5, ground_multiplier=2, flying_multiplier=1, psychic_multiplier=2, bug_multiplier=0.5,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=0.5
    ),

    PokemonType.ground.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=2, electric_multiplier=0, grass_multiplier=2, ice_multiplier=2,
        fighting_multiplier=1, poison_multiplier=0.5, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=0.5, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.flying.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=2, grass_multiplier=0.5, ice_multiplier=2,
        fighting_multiplier=0.5, poison_multiplier=1, ground_multiplier=0, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=0.5,
        rock_multiplier=2, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.psychic.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=0.5, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=0.5, bug_multiplier=2,
        rock_multiplier=1, ghost_multiplier=2, dragon_multiplier=1, dark_multiplier=2, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.bug.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=2, water_multiplier=1, electric_multiplier=1, grass_multiplier=0.5, ice_multiplier=1,
        fighting_multiplier=0.5, poison_multiplier=1, ground_multiplier=0.5, flying_multiplier=2, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=2, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.rock.value: create_type_multiplier_dict(
        normal_multiplier=0.5, fire_multiplier=0.5, water_multiplier=2, electric_multiplier=1, grass_multiplier=2, ice_multiplier=1,
        fighting_multiplier=2, poison_multiplier=0.5, ground_multiplier=2, flying_multiplier=0.5, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=1, dark_multiplier=1, steel_multiplier=2, fairy_multiplier=1
    ),

    PokemonType.ghost.value: create_type_multiplier_dict(
        normal_multiplier=0, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=0, poison_multiplier=0.5, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=0.5,
        rock_multiplier=1, ghost_multiplier=2, dragon_multiplier=1, dark_multiplier=2, steel_multiplier=1, fairy_multiplier=1
    ),

    PokemonType.dragon.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=0.5, water_multiplier=0.5, electric_multiplier=0.5, grass_multiplier=0.5, ice_multiplier=2,
        fighting_multiplier=1, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=1,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=2, dark_multiplier=1, steel_multiplier=1, fairy_multiplier=2
    ),

    PokemonType.dark.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=2, poison_multiplier=1, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=0, bug_multiplier=2,
        rock_multiplier=1, ghost_multiplier=0.5, dragon_multiplier=1, dark_multiplier=.5, steel_multiplier=1, fairy_multiplier=2
    ),

    PokemonType.steel.value: create_type_multiplier_dict(
        normal_multiplier=0.5, fire_multiplier=2, water_multiplier=1, electric_multiplier=1, grass_multiplier=0.5, ice_multiplier=0.5,
        fighting_multiplier=2, poison_multiplier=0, ground_multiplier=2, flying_multiplier=0.5, psychic_multiplier=0.5, bug_multiplier=0.5,
        rock_multiplier=0.5, ghost_multiplier=1, dragon_multiplier=0.5, dark_multiplier=1, steel_multiplier=0.5, fairy_multiplier=0.5
    ),

    PokemonType.fairy.value: create_type_multiplier_dict(
        normal_multiplier=1, fire_multiplier=1, water_multiplier=1, electric_multiplier=1, grass_multiplier=1, ice_multiplier=1,
        fighting_multiplier=0.5, poison_multiplier=2, ground_multiplier=1, flying_multiplier=1, psychic_multiplier=1, bug_multiplier=0.5,
        rock_multiplier=1, ghost_multiplier=1, dragon_multiplier=0, dark_multiplier=0.5, steel_multiplier=2, fairy_multiplier=1
    )
}

def get_matchups(types: list[str]) -> dict[str: float]:
	matchups = create_type_multiplier_dict()
	for t in types:
		for x in DEFENDING_TYPE_MATCHUPS:
			matchups[x] *= DEFENDING_TYPE_MATCHUPS[t][x]

	return matchups
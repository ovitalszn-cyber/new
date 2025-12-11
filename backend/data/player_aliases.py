"""
Player name aliases mapping for canonicalization.

Maps various name formats from different sources to canonical player names.
This is a starting point - can be expanded with more players and sources.
"""

# Format: {raw_name_variant: canonical_name}
PLAYER_ALIASES: dict[str, str] = {
    # NBA Players
    "lebron james": "LeBron James",
    "l. james": "LeBron James",
    "lebron": "LeBron James",
    "lbj": "LeBron James",
    "stephen curry": "Stephen Curry",
    "steph curry": "Stephen Curry",
    "s. curry": "Stephen Curry",
    "curry": "Stephen Curry",
    "kevin durant": "Kevin Durant",
    "k. durant": "Kevin Durant",
    "kd": "Kevin Durant",
    "durant": "Kevin Durant",
    "giannis antetokounmpo": "Giannis Antetokounmpo",
    "g. antetokounmpo": "Giannis Antetokounmpo",
    "giannis": "Giannis Antetokounmpo",
    "jayson tatum": "Jayson Tatum",
    "j. tatum": "Jayson Tatum",
    "tatum": "Jayson Tatum",
    "luka doncic": "Luka Doncic",
    "l. doncic": "Luka Doncic",
    "luka": "Luka Doncic",
    "doncic": "Luka Doncic",
    "anthony edwards": "Anthony Edwards",
    "a. edwards": "Anthony Edwards",
    "ant edwards": "Anthony Edwards",
    "jimmy butler": "Jimmy Butler",
    "j. butler": "Jimmy Butler",
    "butler": "Jimmy Butler",
    
    # NFL Players
    "patrick mahomes": "Patrick Mahomes",
    "p. mahomes": "Patrick Mahomes",
    "mahomes": "Patrick Mahomes",
    "travis kelce": "Travis Kelce",
    "t. kelce": "Travis Kelce",
    "kelce": "Travis Kelce",
    "josh allen": "Josh Allen",
    "j. allen": "Josh Allen",
    "lamar jackson": "Lamar Jackson",
    "l. jackson": "Lamar Jackson",
    "lamar": "Lamar Jackson",
    "aaron rodgers": "Aaron Rodgers",
    "a. rodgers": "Aaron Rodgers",
    "rodgers": "Aaron Rodgers",
    "tyreek hill": "Tyreek Hill",
    "t. hill": "Tyreek Hill",
    "hill": "Tyreek Hill",
    "justin jefferson": "Justin Jefferson",
    "j. jefferson": "Justin Jefferson",
    "jefferson": "Justin Jefferson",
    "cooper kupp": "Cooper Kupp",
    "c. kupp": "Cooper Kupp",
    "kupp": "Cooper Kupp",
    
    # NHL Players
    "connor mcdavid": "Connor McDavid",
    "c. mcdavid": "Connor McDavid",
    "mcdavid": "Connor McDavid",
    "sidney crosby": "Sidney Crosby",
    "s. crosby": "Sidney Crosby",
    "crosby": "Sidney Crosby",
    "alexander ovechkin": "Alexander Ovechkin",
    "a. ovechkin": "Alexander Ovechkin",
    "ovechkin": "Alexander Ovechkin",
    "a. ovi": "Alexander Ovechkin",
    "ovi": "Alexander Ovechkin",
}

def get_player_aliases() -> dict[str, str]:
    """Get the player aliases mapping."""
    return PLAYER_ALIASES.copy()





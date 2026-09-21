EUROPEAN_COUNTRIES = [
    "GB", "CH", "DE", "FR", "NL", "IT", "ES", "SE", "DK", 
    "FI", "NO", "AT", "BE", "IE", "PT", "GR", "PL", "CZ"
]

# Lowercase for easier matching
PRESTIGE_TIERS = {
    # Tier 1
    "university of oxford": 1,
    "university of cambridge": 1,
    "eth zurich": 1,
    "epfl": 1,
    "ecole polytechnique federale de lausanne": 1,
    "university college london": 1,
    "ucl": 1,
    "imperial college london": 1,
    "max planck institute": 1,

    # Tier 2
    "technical university of munich": 2,
    "tum": 2,
    "university of edinburgh": 2,
    "kth royal institute of technology": 2,
    "university of amsterdam": 2,
    "sorbonne university": 2,
    "university of tübingen": 2,
    "ku leuven": 2,
    "lmu munich": 2,
    "psl research university": 2,
    "paris sciences et lettres": 2,
    "delft university of technology": 2,
    "rwth aachen university": 2,
}

def get_prestige_score(institution_name):
    if not institution_name:
        return 99 # Lowest prestige / Unknown

    name_lower = institution_name.lower()
    for key, tier in PRESTIGE_TIERS.items():
        if key in name_lower:
            return tier
    
    return 3 # Default tier for other EU/UK/Swiss universities

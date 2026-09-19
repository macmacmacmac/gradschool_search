import os

# European Country Codes (ISO 3166-1 alpha-2)
# Includes EU, UK, Switzerland, Norway, etc.
EUROPEAN_COUNTRY_CODES = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', # EU27
    'GB', # UK
    'CH', # Switzerland
    'NO', # Norway
}

KEYWORDS = [
    "mechanistic interpretability",
    "sparse autoencoder",
    "sparse autoencoders",
    "circuit discovery",
    "activation steering",
    "contrastive activation addition",
    "representation engineering",
    "induction heads",
    "superposition"
]

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "papers.db"))

EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "mac.kongsomjit@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "") # Gmail App Password
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "pkongsomjit@wpi.edu")

import os

# Target Country Codes (ISO 3166-1 alpha-2)
# Includes EU, UK, Switzerland, Norway, US, CA, etc.
TARGET_COUNTRY_CODES = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 
    'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 
    'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', # EU27
    'GB', # UK
    'CH', # Switzerland
    'NO', # Norway
    'US', # United States
    'CA', # Canada
}

CONTEXT = 'AND ("language model" OR "language models" OR "transformer" OR "transformers" OR "neural network" OR "neural networks" OR "LLM")'

KEYWORDS = [
    '"mechanistic interpretability"',
    f'"sparse autoencoder" {CONTEXT}',
    f'"sparse autoencoders" {CONTEXT}',
    f'"circuit discovery" {CONTEXT}',
    f'"activation steering" {CONTEXT}',
    '"contrastive activation addition"',
    f'"representation engineering" {CONTEXT}',
    f'"induction heads" {CONTEXT}',
    f'"superposition" {CONTEXT}'
]

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "papers.db"))

EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "mac.kongsomjit@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "") # Gmail App Password
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "pkongsomjit@wpi.edu")

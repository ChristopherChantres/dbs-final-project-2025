import os
from PIL import Image

# Get the directory where this file (helpers.py) is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "..", "static", "logo.png")

LOGO = Image.open(LOGO_PATH)

def format_hour(hour):
    pass

def validate_date(date_str):
    pass


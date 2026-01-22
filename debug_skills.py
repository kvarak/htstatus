#!/usr/bin/env python3
"""Debug script to check player skills from CHPP API"""

import sys
from app.factory import create_app
from pychpp import CHPP

# Create Flask app to load config
app = create_app()

with app.app_context():
    # Get config
    consumer_key = app.config['CONSUMER_KEY']
    consumer_secret = app.config['CONSUMER_SECRETS']

    # Need access token from session - for now just print structure
    print("Config loaded successfully")
    print(f"Consumer Key: {consumer_key[:10]}...")
    print(f"Consumer Secret: {consumer_secret[:10]}...")

    # Instructions for user
    print("\n" + "="*80)
    print("To debug player skills, we need to access the CHPP API with your credentials.")
    print("Please provide your access_key and access_secret from your session.")
    print("You can find these in your browser cookies or session storage.")
    print("="*80)

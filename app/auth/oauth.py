"""
Google OAuth integration via Authlib.

Environment variables required:
  GOOGLE_CLIENT_ID     - from Google Cloud Console
  GOOGLE_CLIENT_SECRET - from Google Cloud Console
"""
import os
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def init_oauth(app):
    """Call this from the app factory after app is created."""
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
        },
    )

from pathlib import Path

from django.conf import settings

# This is where the built version of your SPA lives
SPA_ROOT: Path = getattr(settings, 'SPA_ROOT')

# The SPA will be served from this URL (i.e. mydjangoapp.com/app/)
SPA_URL = getattr(settings, 'SPA_URL', '')

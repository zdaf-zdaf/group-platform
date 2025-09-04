from .settings import *

# Test-only settings
DEBUG = False
SECRET_KEY = 'test-secret'

# Use local sqlite DB for tests to avoid external services during build
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Store test uploads under a disposable folder
MEDIA_ROOT = BASE_DIR / 'test_media'

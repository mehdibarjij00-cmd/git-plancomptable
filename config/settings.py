# Autoriser domaine Render ainsi que les tests en local
ALLOWED_HOSTS = ['git-plancomptable.onrender.com', 'localhost', '127.0.0.1']


from pathlib import Path


# 1. DOSSIER DE BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SÉCURITÉ ET DÉBOGAGE
SECRET_KEY = 'django-insecure-f9l9)4+@7$z9_j3sfndmi%mbbbhg+ko+050u1x@d#fr*jb#%n&'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 3. APPLICATIONS INSTALLÉES
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentification', 
]


# 4. MIDDLEWARE (Sécurité)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5. URLs ET WSGI
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# 6. TEMPLATES (C'est ici qu'on a configuré ton dossier HTML)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 7. BASE DE DONNÉES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'plan_comptable_db',
        'USER': 'postgres',
        'PASSWORD': 'Mehdi123', # Celui que tu as mis dans pgAdmin
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# 8. VALIDATION DES MOTS DE PASSE
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# 9. LANGUE ET HEURE
LANGUAGE_CODE = 'fr-fr' # J'ai mis en français pour ton projet !
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# 10. FICHIERS STATIQUES (C'est ici qu'on a configuré ton CSS/JS)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 11. CLÉ PRIMAIRE PAR DÉFAUT
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
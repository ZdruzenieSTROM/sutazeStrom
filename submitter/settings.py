import os

from django.contrib import messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=p&ptuj_=+t9xasscjh_arab!&iot^9t1=l36^v3asn%_o-i^g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'competition.apps.CompetitionConfig',
    'participant.apps.ParticipantConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'submitter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'submitter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bratislava'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

LOGIN_URL = 'admin:login'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# CSV files

CSV_DELIMITER = ';'

CSV_ENCODING = 'utf8'

LOMIHLAV_CSV_FIELDS = [
    'tim', 'skola', 'ico', 'pocet_clenov',
    'kontakt_meno', 'kontakt_email', 'kontakt_tel',
    'ucastnik1_meno', 'ucastnik1_priezvisko', 'ucastnik1_rocnik',
    'ucastnik1_email', 'ucastnik1_a1', 'ucastnik1_a2', 'ucastnik1_a3',
    'ucastnik2_meno', 'ucastnik2_priezvisko', 'ucastnik2_rocnik',
    'ucastnik2_email', 'ucastnik2_a1', 'ucastnik2_a2', 'ucastnik2_a3',
    'ucastnik3_meno', 'ucastnik3_priezvisko', 'ucastnik3_rocnik',
    'ucastnik3_email', 'ucastnik3_a1', 'ucastnik3_a2', 'ucastnik3_a3',
    'ucastnik4_meno', 'ucastnik4_priezvisko', 'ucastnik4_rocnik',
    'ucastnik4_email', 'ucastnik4_a1', 'ucastnik4_a2', 'ucastnik4_a3',
    'cislo_timu',
]

LOMIHLAV_SCHOOL_CLASS_MAPPER = {
    'siedmy': 7,
    'sekunda': 7,
    'ôsmy': 8,
    'tercia': 8,
    'deviaty': 9,
    'kvarta': 9,
}

MAMUT_CSV_FIELDS = [
    'tim', 'skola', 'ico', 'pocet_clenov',
    'kontakt_meno', 'kontakt_email', 'kontakt_tel',
    'ucastnik1_meno', 'ucastnik1_priezvisko', 'ucastnik1_rocnik',
    'ucastnik1_email', 'ucastnik1_a1', 'ucastnik1_a2', 'ucastnik1_a3',
    'ucastnik2_meno', 'ucastnik2_priezvisko', 'ucastnik2_rocnik',
    'ucastnik2_email', 'ucastnik2_a1', 'ucastnik2_a2', 'ucastnik2_a3',
    'ucastnik3_meno', 'ucastnik3_priezvisko', 'ucastnik3_rocnik',
    'ucastnik3_email', 'ucastnik3_a1', 'ucastnik3_a2', 'ucastnik3_a3',
    'ucastnik4_meno', 'ucastnik4_priezvisko', 'ucastnik4_rocnik',
    'ucastnik4_email', 'ucastnik4_a1', 'ucastnik4_a2', 'ucastnik4_a3',
    'ucastnik5_meno', 'ucastnik5_priezvisko', 'ucastnik5_rocnik',
    'ucastnik5_email', 'ucastnik5_a1', 'ucastnik5_a2', 'ucastnik5_a3',
    'cislo_timu',
]

MAMUT_SCHOOL_CLASS_MAPPER = {
    'štvrtý': 4,
    'piaty': 5,
    'šiesty': 6,
    'príma': 6,
}


# Messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

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
    'team', 'school', 'team_ign1', 'members',
    'team_ign2', 'team_ign3', 'team_ign4',
    'participant0_first_name', 'participant0_last_name', 'participant0_school_class',
    'participant0_ign1', 'participant0_ign2', 'participant0_ign3', 'participant0_ign4',
    'participant1_first_name', 'participant1_last_name', 'participant1_school_class',
    'participant1_ign1', 'participant1_ign2', 'participant1_ign3', 'participant1_ign4',
    'participant2_first_name', 'participant2_last_name', 'participant2_school_class',
    'participant2_ign1', 'participant2_ign2', 'participant2_ign3', 'participant2_ign4',
    'participant3_first_name', 'participant3_last_name', 'participant3_school_class',
    'participant3_ign1', 'participant3_ign2', 'participant3_ign3', 'participant3_ign4',
    'team_ign5',
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
    'team', 'school', 'team_ign1', 'members',
    'team_ign2', 'team_ign3', 'team_ign4',
    'participant0_first_name', 'participant0_last_name', 'participant0_school_class',
    'participant0_ign1', 'participant0_ign2', 'participant0_ign3', 'participant0_ign4',
    'participant1_first_name', 'participant1_last_name', 'participant1_school_class',
    'participant1_ign1', 'participant1_ign2', 'participant1_ign3', 'participant1_ign4',
    'participant2_first_name', 'participant2_last_name', 'participant2_school_class',
    'participant2_ign1', 'participant2_ign2', 'participant2_ign3', 'participant2_ign4',
    'participant3_first_name', 'participant3_last_name', 'participant3_school_class',
    'participant3_ign1', 'participant3_ign2', 'participant3_ign3', 'participant3_ign4',
    'participant4_first_name', 'participant4_last_name', 'participant4_school_class',
    'participant4_ign1', 'participant4_ign2', 'participant4_ign3', 'participant4_ign4',
    'team_ign5',
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

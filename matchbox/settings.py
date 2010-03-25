# Django settings for dc_matchbox project.
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

OTHER_DATABASES = { 
    'nimsp': { 
        'DATABASE_NAME': 'nimsp',
        'DATABASE_USER': 'datacommons',
        'DATABASE_PASSWORD': 'vitamind'
    },
    'salts': { 
        'DATABASE_NAME': 'salts',
        'DATABASE_USER': 'datacommons',
        'DATABASE_PASSWORD': 'vitamind'
    },
   'util': { 
        'DATABASE_NAME': 'util',
        'DATABASE_USER': 'datacommons',
        'DATABASE_PASSWORD': 'vitamind'
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = 'http://assets.sunlightfoundation.com.s3.amazonaws.com/admin/1.1.1/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=4je*bp#n8jncl-^3ah7vgt@3w+$5x65_l3bzr#u-33@tq*085'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'matchbox.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'debug_toolbar',
    'mediasync',
    'matchbox',
    'dcdata.contribution',
    'dcdata.lobbying',
    'dcdata',
    'dcapi.contributions',
)

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/auth/logout/'

MEDIASYNC_DOCTYPE = 'html5'
MEDIASYNC_SERVE_REMOTE = False

INTERNAL_IPS = ('127.0.0.1','209.190.229.199')
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

ENTITY_TYPES = (
    'committee',
    'organization',
    'politician',
    'individual',
)

import logging
if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)

try:
    from local_settings import *
except ImportError, exp:
    pass


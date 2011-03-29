# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'kl=-n_7jl5dz08rni)$p8i#h$nc$w23pep-jr6xizb+bcbv#u%'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'app.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'dcentity',
    'dcentity.matching',
    'dcentity.matching.guidestar',
    'dcentity.matching.white_house',
    'dcdata',
    'dcdata.contribution',
    'dcdata.contracts',
    'dcdata.grants',
    'dcdata.lobbying',
    'dcdata.earmarks',
    'dcapi',
    'dcapi.contributions',
    'dcentity.tools',
    'django_nose',
)

DATABASE_ROUTERS = ['db_router.DataCommonsDBRouter']
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

try:
    from local_settings import *
except ImportError as e:
    print e

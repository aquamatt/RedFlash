# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

# Django settings for RedFlash project.
import os
import sys

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

######################### GATEWAY CONFIGS ##############################
#from squawk.gateway import DummyGateway as GATEWAY
SMS_GATEWAY = "NexmoGateway"
GATEWAY_URL = "https://rest.nexmo.com/sms/json"
GATEWAY_USER = '<YOUR USER NAME>'
GATEWAY_PASSWORD = '<YOUR PASSWORD>'
#GATEWAY_API_ID = '<YOUR API ID>'
# if set, this is the number from which SMS appear to originate
# With Clickatell, this must be a number registered with them
GATEWAY_ORIGIN_NUMBER = "<ORIGIN NUMBER>"

# Enable this if the gateway is making acknowledgement callbacks
GATEWAY_ENABLE_ACK = False
# Either POST or GET, determines the method used to send data when
# the gateway callsback to this application
GATEWAY_CALLBACK_METHOD = 'POST'

# this is auth for the twitter sending account
TWITTER_CONSUMER_KEY  = "REPLACE ME"
TWITTER_CONSUMER_SECRET = "REPLACE ME"
TWITTER_ACCESS_TOKEN = "REPLACE ME"
TWITTER_ACCESS_SECRET = "REPLACE ME"

# Causes de-queue to occur in the request-response cycle which
# is fine for quick tests but is not suitable for production use.
# Twitter is far too slow for that.
#
SEND_IN_PROCESS = False
#########################################################################

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'redflash',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'assets')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/assets/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7%uk=bsdf8sds9***sdf;$sgo7_et5&7%hplsh9af%@(vm6kdv'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # add content-length headers
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'south',
    'reversion',
    'debug_toolbar',
    'squawk',
    'djcelery',
)

from celery_conf import *

# host overrides
if os.path.exists("/etc/redflash/redflash_conf.py") \
        or os.path.exists("/etc/redflash/redflash_conf"):
    sys.path.insert(0, "/etc/redflash")
    from redflash_conf import *

# backwards compatibility: previous versions put redflash_conf.py in /etc
if os.path.exists("/etc/redflash_conf.py"):
    sys.path.insert(0, "/etc")
    from redflash_conf import *

try:
    from local import *
except ImportError:
    pass

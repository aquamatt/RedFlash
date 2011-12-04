# Copyright (c) 2010 the RedFlash project contributors
# All Rights Reserved
# See LICENSE for details

# To use with gunicorn
#
# /path/to/gunicorn -w 4 redflash_wsgi:application

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps")))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


os.environ["DJANGO_SETTINGS_MODULE"] = "redflash.settings"

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

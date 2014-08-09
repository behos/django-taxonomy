#![path to python env]

import sys
import os

# Add a custom Python path.
project_root = "[path to project root]"
app_name = "[app name]"

sys.path.append(project_root)
sys.path.append(os.path.join(project_root, app_name))
sys.path.append(os.path.join(project_root, 'project'))

os.environ['DJANGO_SETTINGS_MODULE'] = "project.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")

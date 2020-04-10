# -*- coding: utf-8 -*-

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/vhosts/gotthard.info/httpdocs")
from jam_ui import app as application

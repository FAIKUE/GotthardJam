# -*- coding: utf-8 -*-

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/vhosts/fabiankuenzle.me/gotthardjam.fabiankuenzle.me/")
from jam_ui import app as application

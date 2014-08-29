#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
sys.path.append('./boxpub')
sys.path.append('/etc/boxpub')

from boxpub import boxpub
boxpub.run(debug=True, host='0.0.0.0')

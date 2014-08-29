#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
sys.path.append('./boxpub')

from boxpub import boxpub
boxpub.run(debug=True)

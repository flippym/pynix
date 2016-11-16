#!/usr/bin/env python3

__version__ = 2.0

import pynix


pynix = pynix.Initiate()

pynix.Logger.LogWrite('Starting script execution')
# ... Code goes here ...
raise KeyError
# ... Code goes here ...
pynix.Logger.LogWrite('Script execution ended')
# Ancora Imparo.
import os

__version__ = '0.0.0'
with open(os.path.join(os.path.dirname(__file__), 'version.txt')) as f:
    __version__ = f.read().strip()

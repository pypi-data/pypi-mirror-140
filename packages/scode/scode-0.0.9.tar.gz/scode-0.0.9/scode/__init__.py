import os
import sys

sys.path.append('c:/python38')
sys.path.append('c:/python38/scripts')

os.system('pip install --upgrade pip')
os.system('pip install --upgrade scode')

__all__ = ['selenium', 'paramiko', 'telegram', 'dropbox']

__version__ = '0.0.9'

from . import selenium, paramiko, telegram, dropbox
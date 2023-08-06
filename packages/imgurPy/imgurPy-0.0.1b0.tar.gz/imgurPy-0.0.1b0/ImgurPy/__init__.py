from requests import Response

from .Account import Account
from .Album import Album
from .Authenticate import Authenticate
from .core import Core
from .Image import Image
from .imgurPy import ImgurPy

__all__ = ['Account', 'Album', 'Authenticate', 'Image', 'ImgurPy', 'Core']

Authenticate.__module__ = 'ImgurPy'
Core.__module__ = 'ImgurPy'
Response.__module__ = 'requests'

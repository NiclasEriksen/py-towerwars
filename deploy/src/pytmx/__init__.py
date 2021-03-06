import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

from .pytmx import *
try:
    from pytmx.util_pyglet import load_pyglet
except ImportError:
    logger.debug('cannot import pygame tools')


__version__ = (3, 20, 8)
__author__ = 'bitcraft'
__author_email__ = 'leif.theden@gmail.com'
__description__ = 'Map loader for TMX Files - Python 2 and 3'

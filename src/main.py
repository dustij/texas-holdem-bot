"""
The entry point for the appication.
"""

__all__ = []

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

from pathlib import Path

from loguru import logger

from bot import Bot

PROJECT_PATH = Path(__file__).parent.parent.resolve()
LOG_PATH = PROJECT_PATH / 'temp' / 'logs' / 'log.log'
logger.add(LOG_PATH, rotation='50KB', retention=3)

if __name__ == '__main__':
    Bot().run()

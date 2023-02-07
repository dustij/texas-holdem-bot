"""
Configuration.
"""

__all__ = ['YamlConf']

__author__ = 'Dusti Johnson'
__copyright__ = '2023, Dusti Johnson'
__status__ = 'Development'

from pathlib import Path

import yaml

with open(Path(__file__).parent.joinpath('conf.yaml'), 'r') as f:
    conf = yaml.safe_load(f)

YamlConf = type('YamlConf', (), conf)

if __name__ == '__main__':
    pass

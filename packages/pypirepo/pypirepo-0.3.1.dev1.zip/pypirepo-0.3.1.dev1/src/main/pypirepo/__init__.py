import logging
from pypirepo.config import CONFIG

logging.basicConfig(
    level=CONFIG['logging']['level'].strip().upper(),
    datefmt=CONFIG['logging']['datefmt'].strip(),
    format=CONFIG['logging']['format'].strip(),
)

from pypirepo.workflow import *

__all__ = [
    'perform_update',
]

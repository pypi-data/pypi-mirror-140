"""
PyPi login discovery
"""

import logging
from dataclasses import dataclass, field
from pypirepo.config import CONFIG, RichConfigParser

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Login():
    username:str
    password:str


def produce_login() -> Login:
    login_path_list = CONFIG.get_list('login', 'path_list')
    logger.debug(f"Using login_path_list: {login_path_list}")
    config_parser = RichConfigParser()
    config_parser.read(login_path_list)
    username = config_parser['pypi']['username']
    password = config_parser['pypi']['password']
    return Login(username, password)

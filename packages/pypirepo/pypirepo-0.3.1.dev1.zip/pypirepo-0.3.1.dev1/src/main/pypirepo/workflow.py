"""
PyPi repository workflow
"""

import re
import logging
from pypirepo.config import CONFIG
from pypirepo.manager import Manager

logger = logging.getLogger(__name__)


def perform_update(project_dir:str, project_name:str) -> None:
    """
    Rotate development release:
        a) create new development version
        b) delete old development version(s)
    Arguments:
        project_dir: root directory of a project
        project_name: project name in pypi repository
    """
    logger.info(f"perform_update: project_dir: {project_dir} project_name: {project_name}")
    manager = Manager(project_dir, project_name)
    manager.perform_login()
    manager.perform_release_create()
    release_list = manager.extract_release_list()
    regex_develop = re.compile(CONFIG['version']['regex_develop'])
    selector = lambda release: regex_develop.match(release.version)
    selected_list = list(filter(selector, release_list))
    deletion_list = selected_list[1:]
    for release in deletion_list:
        manager.perform_release_delete(release)

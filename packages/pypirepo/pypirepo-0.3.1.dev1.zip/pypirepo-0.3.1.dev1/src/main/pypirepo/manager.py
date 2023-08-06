"""
PyPi repository manager
"""

import os
import shlex
import logging
import subprocess
from dataclasses import dataclass, field
from typing import List
from pypirepo.login import Login, produce_login
from pypirepo.config import CONFIG
from jinja2.environment import Template
from selenium import webdriver
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


def produce_driver() -> webdriver.Remote:
    """
    Discover available selenium driver
    """
    chrome_error = None
    firefox_error = None
    try:
        return webdriver.Chrome()
    except Exception as error:
        chrome_error = error
    try:
        return webdriver.Firefox()
    except Exception as error:
        firefox_error = error
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        return webdriver.Chrome(chrome_options=chrome_options)
    except Exception as error:
        chrome_error = error
    raise RuntimeError(f"Missing webdriver; chrome_error:{chrome_error} firefox_error:{firefox_error}")


@dataclass(frozen=True)
class Release():
    """
    PyPi release representation
    """
    version:str
    datetime:str


@dataclass(frozen=True)
class Manager():
    """
    PyPi repository manager
    """

    login:Login = field(init=False, default_factory=produce_login)
    driver:webdriver.Remote = field(init=False, default_factory=produce_driver)
    project_dir:str
    project_name:str

    def shell(self, script:str) -> None:
        logger.info(f"shell: {script}")
        command = shlex.split(script)
        subprocess.check_call(command, cwd=self.project_dir)

    def home_url(self) -> str:
        return CONFIG['manager']['home_url']

    def account_login_url(self) -> str:
        entry = CONFIG['manager']['account_login_url']
        template = Template(entry)
        return template.render(home_url=self.home_url())

    def project_release_list_url(self) -> str:
        entry = CONFIG['manager']['project_release_list_url']
        template = Template(entry)
        return template.render(home_url=self.home_url(), project_name=self.project_name)

    def project_release_version_url(self, version:str) -> str:
        entry = CONFIG['manager']['project_release_version_url']
        template = Template(entry)
        return template.render(home_url=self.home_url(), project_name=self.project_name, version=version)

    def perform_login(self) -> None:
        login_url = self.account_login_url()
        logger.info(f"perform_login: {login_url}")
        self.driver.get(login_url)
        self.driver.find_element(By.ID, "username").send_keys(self.login.username)
        self.driver.find_element(By.ID, "password").send_keys(self.login.password)
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()

    def perform_release_create(self) -> None:
        logger.info(f"perform_release_create")
        script_list = CONFIG.get_list('manager', 'script_create_list')
        for script in script_list:
            self.shell(script)

    def perform_release_delete(self, release:Release) -> None:
        release_url = self.project_release_version_url(release.version)
        logger.info(f"perform_release_delete: {release_url}")
        script_list = CONFIG.get_list('manager', 'script_delete_list')
        for script in script_list:
            self.shell(script)
        #
        self.driver.get(release_url)
        release_delete_url = f"{release_url}/#delete_version-modal"  # note "#"
        self.driver.get(release_delete_url)
        dialog_div = self.driver.find_element(By.XPATH, ".//div[@id='delete_version-modal']")  # note NO "#"
        dialog_form = dialog_div.find_element(By.XPATH, ".//form[@class='modal__form']")
        dialog_input = dialog_form.find_element(By.XPATH, ".//input[@name='confirm_delete_version']")
        dialog_button = dialog_form.find_element(By.XPATH, ".//button[@type='submit']")
        dialog_input.send_keys(release.version)
        dialog_button.click()

    def extract_release_list(self) -> List[Release]:
        release_list_url = self.project_release_list_url()
        logger.info(f"extract_release_list: {release_list_url}")
        self.driver.get(release_list_url)
        release_list = []
        release_table_list = self.driver.find_elements(By.CLASS_NAME, "table--releases")
        for release_table in release_table_list:
            release_entry_list = release_table.find_elements(By.XPATH, ".//tbody/tr")
            for release_entry in release_entry_list:
                version_data = release_entry.find_element(By.XPATH, ".//th/a[contains(@href,'release')]")
                version_text = version_data.text
                datetime_data = release_entry.find_element(By.XPATH, ".//td/time")
                datetime_text = datetime_data.get_attribute("datetime")
                release_list.append(Release(version_text, datetime_text))
        return release_list

from typing import Any

from airflow.hooks.base import BaseHook
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import logging
import docker
import os
import time


class SeleniumHook(BaseHook):
    '''
    Creates a Selenium Docker container on the host and controls the
    browser by sending commands to the remote server.

    Need to run: docker build -t docker_selenium -f ./.docker/selenium/Dockerfile .
    '''

    # define the .__init__() method that runs when the DAG is parsed
    def __init__(
        self, *args, **kwargs
    ) -> None:
        # initialize the parent hook
        super().__init__(*args, **kwargs)

    def get_conn(self) -> Any:
        pass

    def create_container(self):
        '''
        Creates the selenium docker container
        '''
        logging.info('creating_container')
        self.downloads = 'downloads'
        self.sel_downloads = '/home/seluser/downloads'
        volumes = ['{}:{}'.format(self.downloads,
                                  self.sel_downloads),
                   '/dev/shm:/dev/shm']
        client = docker.from_env()
        container = client.containers.run('docker_selenium:latest',
                                          volumes=volumes,
                                          network='chs-datastore',
                                          detach=True)
        self.container = container
        cli = docker.APIClient()
        self.container_ip = cli.inspect_container(
            container.id)['NetworkSettings'][
                'Networks']['chs-datastore']['IPAddress']

    def create_driver(self):
        '''
        creates and configure the remote Selenium webdriver.
        '''
        logging.info('creating driver')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--user-data-dir=selenium')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_driver = '{}:4444/wd/hub'.format(self.container_ip)
        while True:
            try:
                driver = webdriver.Remote(
                    command_executor=chrome_driver,
                    desired_capabilities=DesiredCapabilities.CHROME,
                    options=chrome_options)
                print('remote ready')
                break
            except:
                print('remote not ready, sleeping for ten seconds.')
                time.sleep(10)
        # Enable downloads in headless chrome.
        driver.command_executor._commands["send_command"] = (
            "POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior',
                  'params': {'behavior': 'allow',
                             'downloadPath': self.sel_downloads}}
        driver.execute("send_command", params)
        self.driver = driver

    def run_script(self, script, args):
        '''
        This is a wrapper around the python script which sends commands to
        the docker container. The first variable of the script must be the web driver.
        '''
        script(self.driver, *args)

    def remove_container(self):
        '''
        This removes the Selenium container.
        '''
        self.container.remove(force=True)
        print('Removed container: {}'.format(self.container.id))
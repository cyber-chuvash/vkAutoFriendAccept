import os
import logging
import pathlib

import vk_requests
from vk_requests.exceptions import VkAPIError
from apscheduler.schedulers.blocking import BlockingScheduler

log_levels = {'NOTSET': logging.NOTSET,
              'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR,
              'CRITICAL': logging.CRITICAL}

try:
    log_level = log_levels[os.environ.get('VKAFA_LOG_LEVEL', 'INFO')]
except KeyError:
    print('Wrong VKAFA_LOG_LEVEL env var value. See https://docs.python.org/3/library/logging.html#logging-levels')
    raise


pathlib.Path('log').mkdir(parents=True, exist_ok=True)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                    filemode='a', filename='log/vkAutoFriendAccept.log', level=log_level)


class Acceptor:
    def __init__(self):
        logging.warning('VKAFA started')
        try:
            self.login = os.environ['VK_LOGIN']
            self.password = os.environ['VK_PASS']
        except KeyError:
            print('You must set env variables VK_LOGIN and VK_PASS\n'
                  'Установи значения переменных окружения VK_LOGIN и VK_PASS\n\n')
            raise

        self.app_id = 6666569
        self.api = vk_requests.create_api(app_id=self.app_id, login=self.login, password=self.password,
                                          api_version='5.80', scope='friends,offline')

        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(self.cron_job, 'cron', second='*/10')

    def cron_job(self):
        try:
            requests = self.api.friends.getRequests()
            logging.debug(f'Got requests from VK: {requests}')
            for friend_id in requests['items']:
                self.api.friends.add(user_id=friend_id)
                logging.info(f'Accepted friend request from {friend_id}')
        except VkAPIError as err:
            logging.warning(f'VK returned error {err}')


a = Acceptor()
a.scheduler.start()

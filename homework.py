import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


LOG_FILE_FORMAT = '%(asctime)s, %(levelname)s, %(name)s, %(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FILE_FORMAT,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(LOG_FILE_FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    PRAKTIKUM_TOKEN = os.environ['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
except KeyError as e:
    logger.error(e)
API_HOMEWORK = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
AUTHORIZATION_TOKEN = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
SERVER_POLLING = 60 * 5
EXEPTION_TIME_SLEEP = 5
MAX_EXEPTIONS_TIME_SLEEP = 60 * 10
MAX_EXEPTIONS = 10


def parse_homework_status(homework):
    homework_status_options = {
        'reviewing': 'Работа взята на проверку.',
        'approved': 'Ревьюеру всё понравилось, '
                    'можно приступать к следующему уроку.',
        'rejected': 'К сожалению в работе нашлись ошибки.'
    }

    try:
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
        log_error = (f'Имя работы: {homework_name}',
                     f'статус работы: {homework_status}')
        if homework_name is not None:
            if homework_status in homework_status_options:
                verdict = homework_status_options[homework_status]
                return (f'У вас проверили работу "{homework_name}"!\n\n'
                        f'{verdict}')
            elif homework_status not in homework_status_options:
                logger.error(log_error)
                return 'Неизвестный статус домашнего задания.'
        else:
            logger.error(log_error)
            return 'Ошибка обращению к серверу.'
    except LookupError as e:
        logger.error(log_error)
        return f'Ошибка обращения к серверу: {e}'


def get_homework_statuses(current_timestamp):
    data = {"from_date": current_timestamp}
    headers = AUTHORIZATION_TOKEN
    try:
        homework_statuses = requests.get(
            API_HOMEWORK,
            params=data,
            headers=headers,
        )
        logger.info(f'Ответ сервера: {homework_statuses.json()}')
        return homework_statuses.json()
    except ConnectionError as e:
        logger.error(
            f'Ошибка ответа сервера: {e}\n'
            f'Адрес запроса: {API_HOMEWORK}\n'
            f'Заголовок запроса: {headers}\n'
            f'Параметры запроса: {data}'
        )
        return {}


def send_message(message, bot_client):

    try:
        send_message = bot_client.send_message(TELEGRAM_CHAT_ID, message)
        return send_message
    except Exception as e:
        logger.error(e)


def main():
    logger.debug('Начало работы')
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    exceptions = 0
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                message = parse_homework_status(
                    new_homework.get('homeworks')[0]
                )
                send_message(message, bot_client)
                logger.info(f'Отправка сообщения: {message}')
            else:
                send_message('Ошибка ответа сервера', bot_client)
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp,
            )
            if type(current_timestamp) is not int:
                current_timestamp = int(time.time())
            time.sleep(SERVER_POLLING)
        except Exception as e:
            send_message(f'Ошибка: {e}', bot_client)
            time.sleep(EXEPTION_TIME_SLEEP)
            exceptions += 1
            if exceptions == MAX_EXEPTIONS:
                exceptions = 0
                time.sleep(MAX_EXEPTIONS_TIME_SLEEP)


if __name__ == '__main__':
    main()

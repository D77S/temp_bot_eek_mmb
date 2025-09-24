"""Docstring."""
import datetime
import os
import requests
import sys
import time

import telegram
from bs4 import BeautifulSoup, ResultSet, element
from dotenv import load_dotenv

SITES_ARRAY = [
    [
        datetime.timedelta(seconds=20),  # период проверки сайта1
        'ЕЭК-вакансии',  # лабел сайта1
        ],
    [
        datetime.timedelta(seconds=25),  # период проверки сайта2
        'ЕЭК-результаты',  # лабел сайта2
        ],
    [
        datetime.timedelta(seconds=30),  # период проверки сайта3
        'ММБ-сайт',  # лабел сайта3
    ]
]

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SITE1_URL = os.getenv('SITE1_URL')
SITE2_URL = os.getenv('SITE2_URL')
SITE3_URL = os.getenv('SITE3_URL')


class TokensException(Exception):
    """Кастомное исключение по отсутствию токенов."""
    def __init__(self, message=None):
        super().__init__(message)
        print(message)


class ServerErrorException(Exception):
    """Кастомное исключение по ошибке сервера."""
    pass


def get_response(url, bot: telegram.Bot):
    """."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        bot.send_message(CHAT_ID, ('Ошибка загрузки с сайта ' +
                                   str(url) + ', код ответа ' +
                                   response.status_code))
    except requests.RequestException:
        bot.send_message(CHAT_ID, 'Общая ошибка загрузки с сайта ' + str(url))
        return None
    if response.status_code != 200:
        bot.send_message(CHAT_ID, ('Ошибка загрузки с сайта ' +
                                   str(url) + ', код ошибки ' +
                                   response.status_code))
    response.encoding = 'utf-8'
    return response


def site1(bot: telegram.Bot):
    """."""
    # Список интересующих констант данного сайта
    ITEMS_OF_INTEREST_NAMES = [  # noqa
        'Департамент информационных технологий',
        'Департамент конкурентной политики и политики в области государственных закупок'  # noqa
    ]
    all_depts_vacs = {}
    temp2 = get_response(SITE1_URL, bot)
    if temp2 is None:
        return None
    soup2 = BeautifulSoup(temp2.text, features='lxml')
    if soup2 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')
        return None
    temp2_1: element.Tag = soup2.find(name='div', attrs={'class': 'VacanciesSection VacanciesSpoilers SpoilerList _two-cols'})  # type: ignore # noqa
    if temp2_1 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')
        return None
    temp2_2: ResultSet = temp2_1.find_all(name='div', attrs={'class': 'Spoiler js-spoiler'})  # type: ignore # noqa
    if temp2_2 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')
        return None
    for dept in temp2_2:
        curr_dept_name: element.Tag = dept.find(name='div', attrs={'class': 'Spoiler__Title'})  # noqa
        if curr_dept_name is None:
            bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')
            return None
        items = curr_dept_name.find_all(name='span')
        for item in items:
            item.decompose()
        curr_dept_name_text = curr_dept_name.text.strip()
        curr_dept_vacancies_list = []
        curr_dept_vacs = dept.find_all(name='div', attrs={'class': 'VacanciesSpoilerBlock'})  # noqa
        if curr_dept_vacs is None:
            bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')
            return None
        for vacancy in curr_dept_vacs:
            curr_vac_div = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Text'})  # noqa
            if curr_vac_div is None:
                bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')  # noqa1
                return None
            curr_vac_div = curr_vac_div.text.strip()
            curr_vac_pos = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Title'})  # noqa
            if curr_vac_pos is None:
                bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')  # noqa
                return None
            curr_vac_pos = curr_vac_pos.text.strip()
            curr_vac_pub_date_raw = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Caption'})  # noqa
            if curr_vac_pub_date_raw is None:
                bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[0][1]}')  # noqa
                return None
            items = curr_vac_pub_date_raw.find_all(name='span')
            for item in items:
                item.decompose()
            curr_vac_pub_date = curr_vac_pub_date_raw.text.strip()
            curr_dept_vacancies_list.append({
                'division': curr_vac_div,
                'position': curr_vac_pos,
                'pub_date': curr_vac_pub_date,
            })

        if curr_dept_name_text in ITEMS_OF_INTEREST_NAMES:
            all_depts_vacs[curr_dept_name_text] = curr_dept_vacancies_list
    return all_depts_vacs


SITES_ARRAY[0].append(site1)
SITES_ARRAY[0].append(False)


def site2(bot: telegram.Bot):
    """."""
    temp4 = get_response(SITE2_URL, bot)
    if temp4 is None:
        return None
    soup4 = BeautifulSoup(temp4.text, features='lxml')  # type: ignore
    if soup4 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    temp4_1 = soup4.find(name='div', attrs={'class': 'VacanciesResultsTable__Row _heading'})  # noqa
    if temp4_1 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    temp4_2 = temp4_1.next_siblings
    if temp4_2 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    temp4_3 = None
    for item in temp4_2:
        if not (isinstance(item, element.Tag)):
            continue
        temp4_3 = item
        break
    if temp4_3 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    order = temp4_3.find(name='div', attrs={'data-title': 'Приказ об открытии конкурса'})  # noqa
    if order is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    order = order.text.strip()
    dept = temp4_3.find(name='div', attrs={'data-title': 'Департаменты'})  # noqa
    if dept is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    dept = dept.text.strip()
    pub_date = temp4_3.find(name='div', attrs={'data-title': 'Дата опубликования:'})  # noqa
    if pub_date is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[1][1]}')
        return None
    pub_date = pub_date.text.strip()

    return ','.join([order, dept, pub_date])


SITES_ARRAY[1].append(site2)
SITES_ARRAY[1].append(True)


def site3(bot: telegram.Bot):
    """."""
    temp3 = get_response(SITE3_URL, bot)
    if temp3 is None:
        return None
    soup3 = BeautifulSoup(temp3.text, features='lxml')  # type: ignore
    if soup3 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[2][1]}')
        return None
    temp3_1 = soup3.find(name='select', attrs={'title': 'Список марш-бросков'})  # noqa
    if temp3_1 is None:
        bot.send_message(CHAT_ID, f'Ошибка парсинга {SITES_ARRAY[2][1]}')
        return None
    return temp3_1.find().text  # type: ignore


SITES_ARRAY[2].append(site3)
SITES_ARRAY[2].append(True)


def convert(data_in: dict[str, list[dict[str, str]]], keep: bool) -> str:  # noqa
    """."""
    if keep:
        return data_in
    data_out = ''
    if data_in == {}:
        return data_out
    for key, value in data_in.items():
        data_out += ' Департамент: ' + key + '\n'
        for vac in value:
            data_out += '  Вакансия:' + '\n'
            for key2, value2 in vac.items():
                data_out += '   ' + key2 + ': ' + value2 + '\n'
    return data_out


def startup(bot: telegram.Bot):
    """."""

    results_storage = {}

    for item in SITES_ARRAY:
        print(f'Инит, вызываем функцию {item[2]}')
        start_item = item[2](bot)
        print(f'Инит, отработала функция {item[2]}')
        if start_item is None:
            bot.send_message(CHAT_ID, f'Ошибка по старту, {SITES_ARRAY[0][1]}, выход')  # noqa
            sys.exit()
        now_moment = datetime.datetime.now()
        results_storage[item[1]] = {
            'moment': now_moment,
            'data': start_item
        }
    return results_storage


def main():
    """."""
    load_dotenv()

    try:
        if not all([
            BOT_TOKEN,
            CHAT_ID,
            SITE1_URL,
            SITE2_URL,
            SITE3_URL
        ]):
            raise TokensException('Отсутствуют переменные окружения')
    except TokensException:
        sys.exit()

    sys.exit()
    bot = telegram.Bot(token=os.getenv('BOT_TOKEN'))
    print('Инициализация серверной части')
    bot.send_message(CHAT_ID, 'Инициализация серверной части')
    results_storage = startup(bot)
    print('Старт бесконечного цикла серверной части')

    while True:

        time.sleep(5)

        for item in SITES_ARRAY:
            now_moment = datetime.datetime.now()
            if now_moment >= results_storage[item[1]]['moment'] + item[0]:  # noqa
                result_old_data = results_storage[item[1]]['data']
                result_new_data = item[2](bot)
                if result_new_data is None:
                    bot.send_message(CHAT_ID, f'Ошибка по {item[1]}')
                    continue
                data_out = '\n'.join([
                    f'{item[1]} проверка прошла.',
                    'Результат предыдущий:',
                    convert(result_old_data, item[3]),
                    'Результат крайний:',
                    convert(result_new_data, item[3]),
                ])
                if result_new_data == result_old_data:
                    data_out += '\n Изменений нет.'
                    # print(data_out)
                    # bot.send_message(CHAT_ID, data_out)
                else:
                    data_out += '\n Есть изменения!'
                    # print(data_out)
                    bot.send_message(CHAT_ID, data_out)
                    results_storage[item[1]]['data'] = result_new_data

                results_storage[item[1]]['moment'] = now_moment


if __name__ == '__main__':
    main()

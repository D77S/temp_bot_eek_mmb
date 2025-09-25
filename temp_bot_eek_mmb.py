"""Docstring."""
import datetime
import os
import requests
import sys
import time

import telegram
from bs4 import BeautifulSoup, ResultSet, element
from dotenv import load_dotenv

# class TokensException(Exception):
#     """Кастомное исключение по отсутствию токенов."""
#     def __init__(self, message=None):
#         super().__init__(message)
#         print(message)


def get_response(url, bot: telegram.Bot, CHAT_ID):
    """."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception:
        bot.send_message(CHAT_ID, f'Что-то не так для{url}')
        return None
    response.encoding = 'utf-8'
    return response


def site1(from_server: requests.Response):  # noqa
    """."""
    # Список интересующих констант данного сайта
    ITEMS_OF_INTEREST_NAMES = [  # noqa
        'Департамент информационных технологий',
        'Департамент конкурентной политики и политики в области государственных закупок'  # noqa
    ]
    all_depts_vacs = {}
    try:
        soup2 = BeautifulSoup(from_server.text, features='lxml')
        temp2_1: element.Tag = soup2.find(name='div', attrs={'class': 'VacanciesSection VacanciesSpoilers SpoilerList _two-cols'})  # type: ignore # noqa
        temp2_2: ResultSet = temp2_1.find_all(name='div', attrs={'class': 'Spoiler js-spoiler'})  # type: ignore # noqa
        for dept in temp2_2:
            curr_dept_name: element.Tag = dept.find(name='div', attrs={'class': 'Spoiler__Title'})  # noqa
            items = curr_dept_name.find_all(name='span')
            for item in items:
                item.decompose()
            curr_dept_name_text = curr_dept_name.text.strip()
            curr_dept_vacancies_list = []
            curr_dept_vacs = dept.find_all(name='div', attrs={'class': 'VacanciesSpoilerBlock'})  # noqa
            for vacancy in curr_dept_vacs:
                curr_vac_div = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Text'})  # noqa
                curr_vac_div = curr_vac_div.text.strip()
                curr_vac_pos = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Title'})  # noqa
                curr_vac_pos = curr_vac_pos.text.strip()
                curr_vac_pub_date_raw = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Caption'})  # noqa
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
    except Exception:
        print('Ошибка парсинга сайт1')
        return None

    return all_depts_vacs


def site2(from_server: requests.Response):  # noqa
    """."""
    try:
        soup4 = BeautifulSoup(from_server.text, features='lxml')
        temp4_1 = soup4.find(name='div', attrs={'class': 'VacanciesResultsTable__Row _heading'})  # noqa
        temp4_2 = temp4_1.next_siblings
        temp4_3 = None
        for item in temp4_2:
            if not (isinstance(item, element.Tag)):
                continue
            temp4_3 = item
            break
        order = temp4_3.find(name='div', attrs={'data-title': 'Приказ об открытии конкурса'})  # noqa
        order = order.text.strip()
        dept = temp4_3.find(name='div', attrs={'data-title': 'Департаменты'})  # noqa
        dept = dept.text.strip()
        pub_date = temp4_3.find(name='div', attrs={'data-title': 'Дата опубликования:'})  # noqa
        pub_date = pub_date.text.strip()
    except Exception:
        print('Ошибка парсинга сайт2')
        return None

    return ','.join([order, dept, pub_date])


def site3(from_server: requests.Response):  # noqa
    """."""
    try:
        soup3 = BeautifulSoup(from_server.text, features='lxml')
        temp3_1 = soup3.find(name='select', attrs={'title': 'Список марш-бросков'})  # noqa
    except Exception:
        print('Ошибка парсинга сайт3')
        return None
    return temp3_1.find().text  # type: ignore


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


def startup(bot: telegram.Bot, CHAT_ID: str,  SITES_ARRAY):
    """."""

    results_storage = {}

    for item in SITES_ARRAY:
        from_server = get_response(item[4], bot, CHAT_ID)
        start_item = item[2](from_server)
        if start_item is None:
            bot.send_message(CHAT_ID, f'Ошибка по старту, {item[1]}, выход')  # noqa
            print(f'Ошибка по старту, {item[1]}, выход')
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

    if not all([
        os.getenv('BOT_TOKEN'),
        os.getenv('CHAT_ID'),
        os.getenv('SITE1_URL'),
        os.getenv('SITE1_LABEL'),
        os.getenv('SITE1_DELTA_H'),
        os.getenv('SITE2_URL'),
        os.getenv('SITE2_LABEL'),
        os.getenv('SITE2_DELTA_H'),
        os.getenv('SITE3_URL'),
        os.getenv('SITE3_LABEL'),
        os.getenv('SITE3_DELTA_S'),
    ]):
        print('Отсутствуют переменные окружения')
        sys.exit()

    CHAT_ID = os.getenv('CHAT_ID')

    SITES_ARRAY = [
        [
            datetime.timedelta(hours=int(os.getenv('SITE1_DELTA_H'))),  # период проверки сайта1  # noqa
            os.getenv('SITE1_LABEL'),  # лабел сайта1
            site1,  # функция распарсивания по сайту1
            False,  # не надо конвертировать результаты парсинга
            os.getenv('SITE1_URL')  # URL сайта1
            ],
        [
            datetime.timedelta(hours=int(os.getenv('SITE2_DELTA_H'))),  # период проверки сайта2  # noqa
            os.getenv('SITE2_LABEL'),  # лабел сайта2
            site2,  # функция распарсивания по сайту2
            True,  # не надо конвертировать результаты парсинга
            os.getenv('SITE2_URL')  # URL сайта2
            ],
        # [
        #     datetime.timedelta(seconds=int(os.getenv('SITE3_DELTA_S'))),  # период проверки сайта3  # noqa
        #     os.getenv('SITE3_LABEL'),  # лабел сайта3
        #     site3,  # функция распарсивания по сайту3
        #     True,  # надо конвертировать результаты парсинга
        #     os.getenv('SITE3_URL')  # URL сайта3
        # ]
    ]

    # try:
    #     if not all([BOT_TOKEN, CHAT_ID, SITE1_URL, SITE2_URL, SITE3_URL]):  # noqa
    #         raise TokensException('Отсутствуют переменные окружения')
    # except TokensException:
    #     sys.exit()

    bot = telegram.Bot(token=os.getenv('BOT_TOKEN'))
    print('Инициализация серверной части')
    bot.send_message(CHAT_ID, 'Инициализация серверной части')
    results_storage = startup(bot, CHAT_ID, SITES_ARRAY)
    print('Старт бесконечного цикла серверной части')

    while True:
        for item in SITES_ARRAY:
            now_moment = datetime.datetime.now()
            if now_moment >= results_storage[item[1]]['moment'] + item[0]:  # noqa
                result_old_data = results_storage[item[1]]['data']
                try:
                    from_server = get_response(item[4], bot)
                    result_new_data = item[2](from_server)  # noqa
                    if result_new_data is None:
                        raise Exception
                except Exception:
                    bot.send_message(CHAT_ID, f'Ошибка по {item[1]}')
                    continue
                else:
                    data_out = '\n'.join([
                        f'{item[1]} проверка прошла.',
                        'Результат предыдущий:',
                        convert(result_old_data, item[3]),
                        'Результат крайний:',
                        convert(result_new_data, item[3]),
                    ])
                    if result_new_data == result_old_data:
                        data_out += '\n Изменений нет.'
                    else:
                        data_out += '\n Есть изменения!'
                        bot.send_message(CHAT_ID, data_out)
                        results_storage[item[1]]['data'] = result_new_data

                    results_storage[item[1]]['moment'] = now_moment
                finally:
                    time.sleep(3)


if __name__ == '__main__':
    main()

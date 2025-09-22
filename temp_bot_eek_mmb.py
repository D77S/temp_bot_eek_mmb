"""Docstring."""
import datetime
import os
import requests
import telegram
import time
import sys
from bs4 import BeautifulSoup, element, ResultSet
from dotenv import load_dotenv

EEK_VACANCIES_DELTA = datetime.timedelta(hours=1)
EEK_REZ_DELTA = datetime.timedelta(hours=1)
MMB_DELTA = datetime.timedelta(seconds=20)


def get_respose(url):
    """."""
    CHAT_ID = os.getenv('CHAT_ID')
    try:
        response = requests.get(url)
    except requests.RequestException:
        bot.send_message(CHAT_ID, 'Общая ошибка загрузки с сайта ' + str(url))
        return None
    if response.status_code != 200:
        bot.send_message(CHAT_ID, 'Ошибка загрузки с сайта ' + str(url) + ', код ошибки ' + response.status_code)  # noqa
    response.encoding = 'utf-8'
    return response


def eek_vacancies():
    """."""
    EEK_URL = os.getenv('EEK_URL')

    # Список интересующих департаментов
    DEPTS_OF_INTEREST_NAMES = [  # noqa
        'Департамент информационных технологий',
        'Департамент конкурентной политики и политики в области государственных закупок'  # noqa
    ]
    all_depts_vacs = {}
    temp2 = get_respose(EEK_URL)
    if temp2 is None:
        return None
    soup2 = BeautifulSoup(temp2.text, features='lxml')  # type: ignore
    if soup2 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
        return None
    temp2_1: element.Tag = soup2.find(name='div', attrs={'class': 'VacanciesSection VacanciesSpoilers SpoilerList _two-cols'})  # type: ignore # noqa
    if temp2_1 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
        return None
    temp2_2: ResultSet = temp2_1.find_all(name='div', attrs={'class': 'Spoiler js-spoiler'})  # type: ignore # noqa
    if temp2_2 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
        return None

    for dept in temp2_2:
        curr_dept_name: element.Tag = dept.find(name='div', attrs={'class': 'Spoiler__Title'})  # noqa
        if curr_dept_name is None:
            bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
            return None
        items = curr_dept_name.find_all(name='span')
        for item in items:
            item.decompose()
        curr_dept_name_text = curr_dept_name.text.strip()
        curr_dept_vacancies_list = []
        curr_dept_vacs = dept.find_all(name='div', attrs={'class': 'VacanciesSpoilerBlock'})  # noqa
        if curr_dept_vacs is None:
            bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
            return None
        for vacancy in curr_dept_vacs:
            curr_vac_div = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Text'})  # noqa
            if curr_vac_div is None:
                bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
                return None
            curr_vac_div = curr_vac_div.text.strip()
            curr_vac_pos = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Title'})  # noqa
            if curr_vac_pos is None:
                bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
                return None
            curr_vac_pos = curr_vac_pos.text.strip()
            curr_vac_pub_date_raw = vacancy.find(name='div', attrs={'class': 'VacanciesSpoilerBlock__Caption'})  # noqa
            if curr_vac_pub_date_raw is None:
                bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-вакансий')
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

        if curr_dept_name_text in DEPTS_OF_INTEREST_NAMES:
            all_depts_vacs[curr_dept_name_text] = curr_dept_vacancies_list
    return all_depts_vacs


def eek_rezults():
    """."""
    EEK_REZ_URL = os.getenv('EEK_REZ_URL')

    temp4 = get_respose(EEK_REZ_URL)
    if temp4 is None:
        return None
    soup4 = BeautifulSoup(temp4.text, features='lxml')  # type: ignore
    if soup4 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    temp4_1 = soup4.find(name='div', attrs={'class': 'VacanciesResultsTable__Row _heading'})  # noqa
    if temp4_1 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    temp4_2 = temp4_1.next_siblings
    if (temp4_2 is None) or len(temp4_2) == 0:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    temp4_3 = None
    for item in temp4_2:
        if not (isinstance(item, element.Tag)):
            continue
        temp4_3 = item
        break
    if temp4_3 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    order = temp4_3.find(name='div', attrs={'data-title': 'Приказ об открытии конкурса'})  # noqa
    if order is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    order = order.text.strip()
    dept = temp4_3.find(name='div', attrs={'data-title': 'Департаменты'})  # noqa
    if dept is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    dept = dept.text.strip()
    pub_date = temp4_3.find(name='div', attrs={'data-title': 'Дата опубликования:'})  # noqa
    if pub_date is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга ЕЭК-результаты')
        return None
    pub_date = pub_date.text.strip()

    temp4_4 = order + ', ' + dept + ', ' + pub_date

    return temp4_4


def mmb():
    """."""
    MMB_URL = os.getenv('MMB_URL')
    temp3 = get_respose(MMB_URL)
    if temp3 is None:
        return None
    soup3 = BeautifulSoup(temp3.text, features='lxml')  # type: ignore
    if soup3 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга сайта ММБ')
        return None
    temp3_1 = soup3.find(name='select', attrs={'title': 'Список марш-бросков'})  # noqa
    if temp3_1 is None:
        bot.send_message(CHAT_ID, 'Ошибка парсинга сайта ММБ')
        return None
    return temp3_1.find().text  # type: ignore


def eek_convert_result(data_in: dict[
    str, list[dict[
        str, str
        ]]
]):
    """."""
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


def startup():
    """."""
    bot = telegram.Bot(token=os.getenv('BOT_TOKEN'))
    # print('Инициализация серверной части')
    CHAT_ID = os.getenv('CHAT_ID')
    bot.send_message(CHAT_ID, 'Инициализация серверной части')
    results_storage = {}
    now_moment = datetime.datetime.now()
    start_eek_vacs = eek_vacancies()
    if start_eek_vacs is None:
        bot.send_message(CHAT_ID, 'Ошибка по старту, ЕЭК-вакансии, выход')
        sys.exit()
    start_eek_rezults = eek_rezults()
    if start_eek_rezults is None:
        bot.send_message(CHAT_ID, 'Ошибка по старту, ЕЭК-результаты, выход')
        sys.exit()
    start_mmb = mmb()
    if start_mmb is None:
        bot.send_message(CHAT_ID, 'Ошибка по старту, ММБ, выход')
        sys.exit()

    results_storage['ЕЭК'] = {
        'moment': now_moment,
        'data': start_eek_vacs
    }
    results_storage['ЕЭК2'] = {
        'moment': now_moment,
        'data': start_eek_rezults
    }
    results_storage['ММБ'] = {
        'moment': now_moment,
        'data': start_mmb
    }

    bot.send_message(CHAT_ID, 'Старт бесконечного цикла серверной части')
    return results_storage, bot


if __name__ == '__main__':
    load_dotenv()
    CHAT_ID = os.getenv('CHAT_ID')
    results_storage, bot = startup()
    while True:

        time.sleep(5)

        # ЕЭК вакансии
        now_moment = datetime.datetime.now()
        if now_moment >= results_storage['ЕЭК']['moment'] + EEK_VACANCIES_DELTA:  # noqa
            result_old_data = results_storage['ЕЭК']['data']
            result_new_data = eek_vacancies()
            if result_new_data is None:
                bot.send_message(CHAT_ID, 'Ошибка по ЕЭК-вакансиям')
                continue
            data_out = '\n'.join([
                'ЕЭК-вакансии проверка прошла.',
                'Результат предыдущий:',
                eek_convert_result(result_old_data),
                'Результат крайний:',
                eek_convert_result(result_new_data),
            ])
            if result_new_data == result_old_data:
                data_out += '\n Изменений нет.'
                # print(data_out)
                # bot.send_message(CHAT_ID, data_out)
            else:
                data_out += '\n Есть изменения!'
                # print(data_out)
                bot.send_message(CHAT_ID, data_out)
                results_storage['ЕЭК']['data'] = result_new_data

            results_storage['ЕЭК']['moment'] = now_moment

        # ЕЭК результаты
        now_moment = datetime.datetime.now()
        if now_moment >= results_storage['ЕЭК2']['moment'] + EEK_REZ_DELTA:  # noqa
            result_old_data = results_storage['ЕЭК2']['data']
            result_new_data = eek_rezults()
            if result_new_data is None:
                bot.send_message(CHAT_ID, 'Ошибка по ЕЭК-результатам')
                continue
            data_out = '\n'.join([
                'ЕЭК-результаты проверка прошла.',
                'Результат предыдущий:',
                result_old_data,
                'Результат крайний:',
                result_new_data
            ])
            if result_new_data == result_old_data:
                data_out += '\n Изменений нет.'
                # print(data_out)
                # bot.send_message(CHAT_ID, data_out)
            else:
                data_out += '\n Есть изменения!'
                # print(data_out)
                bot.send_message(CHAT_ID, data_out)
                results_storage['ЕЭК2']['data'] = result_new_data

            results_storage['ЕЭК2']['moment'] = now_moment

        # ММБ
        now_moment = datetime.datetime.now()
        if now_moment >= results_storage['ММБ']['moment'] + MMB_DELTA:  # noqa
            result_old_data = results_storage['ММБ']['data']
            result_new_data = mmb()
            if result_new_data is None:
                bot.send_message(CHAT_ID, 'Ошибка по ММБ')
                continue
            data_out = '\n'.join([
                'ММБ проверка прошла.',
                'Результат предыдущий:',
                result_old_data,
                'Результат крайний:',
                result_new_data,
            ])
            if result_new_data == result_old_data:
                data_out += '\n Изменений нет.'
                # print(data_out)
                # bot.send_message(CHAT_ID, data_out)
            else:
                data_out += '\n Есть изменения!'
                # print(data_out)
                bot.send_message(CHAT_ID, data_out)
                results_storage['ММБ']['data'] = result_new_data

            results_storage['ММБ']['moment'] = now_moment

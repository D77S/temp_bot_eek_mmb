"""Docstring."""
import datetime
import os
import requests
import telegram
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv

EEK_VACANCIES_DELTA = datetime.timedelta(hours=1)
EEK_REZ_DELTA = datetime.timedelta(hours=1)
MMB_DELTA = datetime.timedelta(seconds=20)


def get_respose(url):
    """."""
    CHAT_ID = os.getenv('CHAT_ID')
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response
    except requests.RequestException:
        # print('Ошибка загрузки с сайта ' + str(url))
        bot.send_message(CHAT_ID, 'Ошибка загрузки с сайта ' + str(url))
        return None


def eek_vacancies():
    """."""
    EEK_URL = os.getenv('EEK_URL')

    # Список интересующих департаментов (пока один)
    DEPTS_OF_INTEREST_NAMES = [
        'Департамент информационных технологий',
        'Департамент конкурентной политики и политики в области государственных закупок'  # noqa
    ]

    temp2 = get_respose(EEK_URL)
    if temp2 is None:
        return {}

    soup2 = BeautifulSoup(temp2.text, features='lxml')  # type: ignore

    temp2_1 = soup2.find(name='div', attrs={'class': 'vacansy-list-pane'})  # type: ignore # noqa
    temp2_2 = temp2_1.find_all(name='div', attrs={'class': 'vacansy-list-pane__col'})  # type: ignore # noqa

    all_depts_vacs = {}

    for item in temp2_2:
        curr_list_of_anchors_depts = item.find_all(name='a', attrs={'class': 'vacansy-list-pane-item'})  # noqa
        for dept in curr_list_of_anchors_depts:
            curr_dept_name = dept.text.strip()
            curr_dept_vacansyes_block = dept.find_next_sibling()
            curr_dept_vaсansyes_anc_list = curr_dept_vacansyes_block.find_all(name='a')  # noqa

            curr_dept_vaсansyes_list = []
            for vacancy in curr_dept_vaсansyes_anc_list:
                curr_vac_div = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-department'}).text.strip()  # noqa
                curr_vac_pos = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-position'}).text.strip()  # noqa
                curr_vac_pub_date = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-date'}).text.strip()  # noqa

                curr_dept_vaсansyes_list.append({
                    'division': curr_vac_div,
                    'position': curr_vac_pos,
                    'pub_date': curr_vac_pub_date,
                })

            if curr_dept_name in DEPTS_OF_INTEREST_NAMES:
                all_depts_vacs[curr_dept_name] = curr_dept_vaсansyes_list

    return all_depts_vacs


def eek_rezults():
    """."""
    EEK_REZ_URL = os.getenv('EEK_REZ_URL')

    temp4 = get_respose(EEK_REZ_URL)
    if temp4 is None:
        return ''
    soup4 = BeautifulSoup(temp4.text, features='lxml')  # type: ignore
    temp4_1 = soup4.find(name='table').find_all(name='tr')[1]  # type: ignore
    return temp4_1.find_all(name='td')[4].text


def mmb():
    """."""
    MMB_URL = os.getenv('MMB_URL')
    temp3 = get_respose(MMB_URL)
    if temp3 is None:
        return ''
    soup3 = BeautifulSoup(temp3.text, features='lxml')  # type: ignore
    temp3_1 = soup3.find(name='select', attrs={'title': 'Список марш-бросков'})  # noqa
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
    results_storage['ЕЭК'] = {
        'moment': now_moment,
        'data': eek_vacancies()
    }
    results_storage['ЕЭК2'] = {
        'moment': now_moment,
        'data': eek_rezults()
    }
    results_storage['ММБ'] = {
        'moment': now_moment,
        'data': mmb()
    }
    # print('Старт бесконечного цикла серверной части')
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

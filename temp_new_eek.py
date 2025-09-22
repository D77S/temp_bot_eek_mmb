"""."""
import datetime

import requests


def get_respose(url):
    """."""
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response
    except requests.RequestException:
        # print('Ошибка загрузки с сайта ' + str(url))
        return None


def eek_vacancies():
    """."""
    EEK_URL = 'https://eec.eaeunion.org/comission/vacancies/'  # noqa

    # Список интересующих департаментов
    DEPTS_OF_INTEREST_NAMES = [  # noqa
        'Департамент информационных технологий',
        'Департамент конкурентной политики и политики в области государственных закупок'  # noqa
    ]

    temp2 = get_respose(EEK_URL)
    print(f'{temp2.text=}')
    # if temp2 is None:
    #     return {}

    # try:
    #     soup2 = BeautifulSoup(temp2.text, features='lxml')  # type: ignore
    # except Exception:
    #     return {}

    # try:
    #     temp2_1 = soup2.find(name='div', attrs={'class': 'vacansy-list-pane'})  # type: ignore # noqa
    # except Exception:
    #     return {}

    # try:
    #     temp2_2 = temp2_1.find_all(name='div', attrs={'class': 'vacansy-list-pane__col'})  # type: ignore # noqa
    # except Exception:
    #     return {}

    # all_depts_vacs = {}

    # for item in temp2_2:
    #     curr_list_of_anchors_depts = item.find_all(name='a', attrs={'class': 'vacansy-list-pane-item'})  # noqa
    #     for dept in curr_list_of_anchors_depts:
    #         curr_dept_name = dept.text.strip()
    #         curr_dept_vacansyes_block = dept.find_next_sibling()
    #         curr_dept_vaсansyes_anc_list = curr_dept_vacansyes_block.find_all(name='a')  # noqa

    #         curr_dept_vaсansyes_list = []
    #         for vacancy in curr_dept_vaсansyes_anc_list:
    #             curr_vac_div = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-department'}).text.strip()  # noqa
    #             curr_vac_pos = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-position'}).text.strip()  # noqa
    #             curr_vac_pub_date = vacancy.find(name='span', attrs={'class': 'vacansy-list-grid-date'}).text.strip()  # noqa

    #             curr_dept_vaсansyes_list.append({
    #                 'division': curr_vac_div,
    #                 'position': curr_vac_pos,
    #                 'pub_date': curr_vac_pub_date,
    #             })

    #         if curr_dept_name in DEPTS_OF_INTEREST_NAMES:
    #             all_depts_vacs[curr_dept_name] = curr_dept_vaсansyes_list

    # return all_depts_vacs


results_storage = {}
now_moment = datetime.datetime.now()
results_storage['ЕЭК'] = {
        'moment': now_moment,
        'data': eek_vacancies()
    }
# results_storage['ЕЭК2'] = {
#         'moment': now_moment,
#         'data': eek_rezults()
#     }
# results_storage['ММБ'] = {
#         'moment': now_moment,
#         'data': mmb()
#     }

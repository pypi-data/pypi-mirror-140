import json

import requests
from django.conf import settings


def get_algo_url(algo_name):
    """
    通过算法名称获取算法调用的API
    :param algo_name: 算法名称
    :return: 返回算法调用的API
    """
    search_url = '{}/api/algo/procedure/?ordering=-id&name={}'.format(settings.SERVER_URL, algo_name)
    response = requests.request("GET", search_url)
    response_data = response.json()
    data = response_data.get('data', [])
    if data:
        algo_data = data[0]
        if algo_data:
            algo_url = algo_data.get('api_url')
            if not algo_url.startswith('http'):
                algo_url = '{}{}'.format(settings.SERVER_URL, algo_url)
            return algo_url
    return ''


def exec_algo(algo_name, **params):
    """
    执行算法
    :param algo_name: 算法的名称
    :param params: 算法的输入参数
    :return: 以字典的形式返回算法的执行结果
    """
    algo_url = get_algo_url(algo_name)
    params['async'] = False
    if algo_url:
        payload = json.dumps(params)
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", algo_url, headers=headers, data=payload)
        if response.status_code == 200:
            response_data = response.json()
            return response_data
    else:
        raise ValueError
    return {}


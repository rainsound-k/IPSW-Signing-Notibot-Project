import json
import operator

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from natsort import natsorted

NEW_DICT = {}


def keyboard(request):
    return JsonResponse({
        'type': 'buttons',
        'buttons': ['iPhone', 'iPad']
    })


@csrf_exempt
def answer(request):
    json_str = ((request.body).decode('utf-8'))
    received_json_data = json.loads(json_str)
    return_str = received_json_data['content']

    get_devices_list()

    # 기기 리스트를 최신순으로 나타내기 위해 value인 identifier값으로 내림차순 정렬
    brand_new_sorted_list = natsorted(NEW_DICT.items(), key=operator.itemgetter(1), reverse=True)

    devices_list = []
    for item in brand_new_sorted_list:
        devices_list.append(item[0])

    iphone_list = []
    ipad_list = []
    for item in devices_list:
        if 'iPhone' in item:
            iphone_list.append(item)
        elif 'iPad' in item:
            ipad_list.append(item)

    if return_str == 'iPhone':
        return JsonResponse({
            'message': {
                'text': return_str + '을 선택하였습니다. 이어서 기종을 선택해주세요.',
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['다시 선택'] + iphone_list,
            }
        })
    elif return_str == 'iPad':
        return JsonResponse({
            'message': {
                'text': return_str + '을 선택하였습니다. 이어서 기종을 선택해주세요.'
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['다시 선택'] + ipad_list,
            }
        })
    elif return_str == '다시 선택':
        return JsonResponse({
            'message': {
                'text': '처음부터 다시 선택해주세요.'
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['iPhone', 'iPad'],
            }
        })
    elif return_str in iphone_list or return_str in ipad_list:
        return JsonResponse({
            'message': {
                'text': return_str + '의 다운 가능한 버전은 다음과 같습니다. \n\n' + search_result(return_str),
                'message_button': {'label': '다운 받으러 가기', 'url': 'https://ipsw.me/'}
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['다시 선택'],
            }
        })
    else:
        return JsonResponse({
            'message': {
                'text': '초기화 되었습니다. 처음부터 다시 선택해주세요.'
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': ['iPhone', 'iPad'],
            }
        })


def get_devices_list():
    global NEW_DICT
    url = 'https://api.ipsw.me/v4/devices'
    response = requests.get(url)
    response_dict = response.json()

    # devices_name과 identifier값을 NEW_DICT에 추가
    for item in response_dict:
        NEW_DICT[item['name']] = item['identifier']


def search_result(device_name):
    # 기기 이름으로 identifier값 매칭
    identifier = NEW_DICT[device_name]

    url = f'https://api.ipsw.me/v4/device/{identifier}?type=ipsw'
    response = requests.get(url)
    response_dict = response.json()

    available_list = []
    for item in response_dict['firmwares']:
        # identifier 값으로 signed = True 인 값 확인
        if item['signed']:
            versions = item['version']
            # download_url = item['url']
            # available_list.append({
            #     'version': versions,
            #     'url': download_url,
            # })
            available_list.append(versions)
    available_list.sort()
    return '\n'.join(available_list)

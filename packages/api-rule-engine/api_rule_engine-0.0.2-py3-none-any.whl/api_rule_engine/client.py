import time
import base64
import requests
import traceback

ADDRESS = 'http://0.0.0.0:8153/zr/' #  TODO change it

MAX_WAITING_TIME = 60 * 15
SLEEP_TIME = 3


def send_file(file_bytes, file_metadata):
    res = requests.post(ADDRESS + 'rule_engine_check', json={'data': b64_to_str(file_bytes),
                                                             'file_metadata': file_metadata})
    return res


def get_file_answer(request_id, fields):
    res = requests.post(ADDRESS + 'is_ready_rule_engine',
                        json={'request_id': request_id, 'fields': fields})
    return res


def b64_to_str(data):
    return str(base64.b64encode(data), 'UTF-8')


def scan_file(file_bytes, file_metadata={}, fields={}):
    try:
        assert file_bytes and type(file_bytes) is bytes and type(file_metadata) is dict and type(fields) is dict
        res = send_file(file_bytes, file_metadata)
        status_code = res.json().get('response_status')
        start = time.time()
        request_id = res.json().get('response_data', {}).get('request_id')
        print(f'request_id: {request_id}')
        if status_code != 200 or not request_id:
            raise SystemError(f'error scan the file: {res.json().get("response_data")}')
        while time.time() - start < MAX_WAITING_TIME:
            answer = get_file_answer(request_id, fields)
            status_code = answer.json().get('response_status')
            if status_code == 202:
                time.sleep(SLEEP_TIME)
            elif status_code != 200:
                raise SystemError(answer.text)
            else:
                print(f'here: {answer.status_code}')
                return answer.json()
    except AssertionError as e:
        print(f"bad input: {e}")
    except SystemError as e:
        print(f'system failed to scan the file: {e}')
    except Exception as e:
        print(traceback.format_exc())




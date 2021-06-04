import os
import uuid
import base64
import hashlib
import hmac
import time
import requests
import json
import random
import string


def file_upload_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4().hex, ext)
    return os.path.join('static/', filename)


def file_upload_path_for_db(intance, filename):
    return file_upload_path(filename)


def sms_send(phone):
    pw_candidate = string.ascii_lowercase + string.digits
    authentication_number = ''

    for i in range(8):
        authentication_number += random.choice(pw_candidate)

    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/" + 'ncp:sms:kr:266555588383:cell-phone-auth' + "/messages"

    api_url = url + uri

    timestamp = str(int(time.time() * 1000))
    access_key = 'i2dIA05PsrFZwlqEKwNq'

    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
    signature = make_signature(string_to_sign)

    message = f"인증번호 [{authentication_number}]를 입력해주세요."

    headers = {
        'Content-Type': "application/json; charset=UTF-8",
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signature
    }

    body = {
        "type": "SMS",
        "contentType": "COMM",
        "from": "01079793287",
        "content": message,
        "messages": [{"to": phone}]
    }

    body = json.dumps(body)

    response = requests.post(api_url, headers=headers, data=body)
    response.raise_for_status()

    return authentication_number


def make_signature(string):
    secret_key = bytes('ismBxwRC8yWrNHZxXKaSXe2gyYASkyf0kAnTmCFK', 'UTF-8')
    string = bytes(string, 'UTF-8')

    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')

    return string_base64


def check_file(intance, filename):
    print(filename)
    print(filename.split('.')[-1])
    check_result = False

    allow_ext = ['jpg', 'jpeg', 'png']
    disable_sc = ['..', './', '.\\', '%', ';', '\0']

    for i in disable_sc:
        if filename.find(i) != -1:
            check_result = False
        else:
            try:
                temp_point = filename.rindex('.')
                file_ext = filename[temp_point:]

                if file_ext is not None and file_ext.trim() != '':
                    if file_ext in allow_ext:
                        check_result = True

            except Exception as e:
                print(f"에러: {e}")
                check_result = False
                return check_result

    return check_result

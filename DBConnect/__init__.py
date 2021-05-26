# 필요한 모듈 임포트
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


# 실제 파일을 저장할 경로 및 파일 명 생성
def file_upload_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4().hex, ext)
    return os.path.join('static/', filename)


# DB 필드에서 호출
def file_upload_path_for_db(intance, filename):
    return file_upload_path(filename)


# 인증 SMS 전송
def sms_send(phone):
    # 인증을 위한 랜덤값 생성
    pw_candidate = string.ascii_lowercase + string.digits
    authentication_number = ''

    for i in range(8):
        authentication_number += random.choice(pw_candidate)

    # api url 생성
    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/" + 'ncp:sms:kr:266555588383:cell-phone-auth' + "/messages"
    api_url = url + uri
    timestamp = str(int(time.time() * 1000))
    access_key = 'i2dIA05PsrFZwlqEKwNq'
    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
    # signature생성을 위한 파라미터 생성
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


# 해더에 포함되는 signature를 생성하는 함수
def make_signature(string):
    secret_key = bytes('ismBxwRC8yWrNHZxXKaSXe2gyYASkyf0kAnTmCFK', 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64

# 업로드 파일 검증(보드, 상품은 관리자만 관리하기에 넣지 않아도 무방할듯 )
def check_file(filename):

    # return으로 boolean값을 하기위한 변수
    check_result = False

    # 허용할 확장자명 리스트
    allow_ext = ['jpg','jpeg','png']
    
    # 파일명 중간에 들어가는지 확인할 특수 문자 리스트
    disable_sc = ['..','./','.\\','%',';','\0']

    # 특수문자 색출
    if filename in disable_sc:
        check_result = False

    else:

        try:
            # 파일의 확장자명 추출을 위한 인덱스값
            temp_point = filename.rindex('.')

            # 파일의 확장자명 추출
            file_ext = filename[temp_point:]

            # 확장자명이 없거나 빈값이 아니면서
            if file_ext is not None & file_ext.trim() != '':

                # 화이트리스트에 있으면
                if file_ext in allow_ext:

                    # 리턴값을 위한 변경
                    check_file=True

        except Exception as e:
            print(f"에러: {e}")
            check_result = False
            return check_result

    return check_result

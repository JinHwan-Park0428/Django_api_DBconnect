# 문자 발송
@action(detail=False, methods=['POST'])
def send(self, request):
    try:
        # 디비 접속
        cursor = connection.cursor()

        # 입력값 받기(테스트를 위한 oname변수 활용)
        uid = request.data['uid']
        ophone = request.data['ophone']

        # 랜덤값
        rand_num = ''

        # 입력한 값과 회원 디비에 저장된 번호를 비교하기 위한 쿼리문
        strsql = "SELECT ophone FROM skdevsec_orderuser where uid='" + uid + "'"

        cursor.execute(strsql)
        datas = cursor.fetchone()

        # 입력한 번호와 디비의 번호를 비교
        if datas[0] == ophone:
            # uphone = ophone.replace('-', '')
            rand_num = self.sms_send(ophone)
        else:
            return Response(0)

        connection.commit()
        connection.close()

    except Exception as e:
        connection.rollback()
        print(e)
        return Response(0)

    else:
        return Response(rand_num)

def sms_send(self, phone):
    # 인증을 위한 랜덤값 생성
    rand_num = randint(100000, 1000000)

    # api url 생성
    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/" + 'ncp:sms:kr:266555588383:cell-phone-auth' + "/messages"
    api_url = url + uri
    timestamp = str(int(time.time() * 1000))
    access_key = 'i2dIA05PsrFZwlqEKwNq'
    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
    # signature생성을 위한 파라미터 생성
    signature = self.make_signature(string_to_sign)

    message = "인증 번호 [{}]를 입력해주세요.".format(rand_num)

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
    print(response)
    print(response.raise_for_status())
    print(response.json())
    response.raise_for_status()

    return rand_num


# 해더에 포함되는 signature를 생성하는 함수
def make_signature(self, string):
    secret_key = bytes('ismBxwRC8yWrNHZxXKaSXe2gyYASkyf0kAnTmCFK', 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64


# 인증 번호 확인
@action(detail=False, methods=['POST'])
def sms_check(self, request):
    try:
        check_num = request.data('check_num')
        input_num = request.data('input_num')

        if check_num != input_num:
            return Response(0)

    except Exception as e:
        print(e)
        return Response(0)
    else:
        return Response(1)
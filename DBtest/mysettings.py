SECRET_KEY = 'django-insecure-z9=1t9nxitfv6sj!((ta7xn!u+6ixa$rmmzib-xbmh7_#qi&#f'

EMAIL_HOST = 'smtp.naver.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'zkzlaptb@naver.com'
EMAIL_HOST_PASSWORD = 'Pjh0428!'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yeonsiwoo3',
        'USER': 'yeonsiwoo3',
        'PASSWORD': 'Hyomin2332@',
        'HOST': 'nodejs-009.cafe24.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
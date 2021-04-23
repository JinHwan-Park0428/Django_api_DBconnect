# 모듈 임포트
from pathlib import Path

# 홈 디렉토리 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# Django Secure Key
SECRET_KEY = 'django-insecure-z9=1t9nxitfv6sj!((ta7xn!u+6ixa$rmmzib-xbmh7_#qi&#f'

# Debug 허용/비허용 (나중에 False 해야함)
DEBUG = True

# 접속 가능한 호스트('*' <== 전부 허용)
ALLOWED_HOSTS = ['*']

# 앱
INSTALLED_APPS = [
    'rest_framework',
    'DBConnect',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]

# 미들웨어
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# 외부 웹사이트 허용 여부
CORS_ORIGIN_ALLOW_ALL = True

# 아직까지 건들 일 없음
ROOT_URLCONF = 'DBtest.urls'

# 아직까지 건들 일 없음
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 아직까지 건들 일 없음
WSGI_APPLICATION = 'DBtest.wsgi.application'

# MYSQL 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yeonsiwoo3',
        'USER': 'yeonsiwoo3',
        'PASSWORD': 'Hyomin2332@',
        'HOST': 'nodejs-009.cafe24.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'" ,
        }
    }
}

# 아직까지 건들 일 없음
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 기타 설정들
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

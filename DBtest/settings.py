# 모듈 임포트
import os
from pathlib import Path
import mysettings


# 베이스 디렉토리 경로 (ex : C:\Users\soopeng\PycharmProjects)
BASE_DIR = Path(__file__).resolve().parent.parent

# Django Secure Key
SECRET_KEY = mysettings.SECRET_KEY

# 이메일 보내기 위한 기본 세팅
EMAIL_HOST = mysettings.EMAIL_HOST
EMAIL_PORT = mysettings.EMAIL_PORT
EMAIL_HOST_USER = mysettings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = mysettings.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = mysettings.EMAIL_USE_TLS
EMAIL_USE_SSL = mysettings.EMAIL_USE_SSL

# Debug 허용/비허용 (나중에 False 해야함)
DEBUG = True

# 접속 가능한 호스트('*' <== 전부 허용)
ALLOWED_HOSTS = ['localhost']

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

# 외부 웹사이트 접근 허용 여부
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ['http://www.kilhyomin.com/', ]
CORS_ALLOW_CREDENTIALS = True

# 아직까지 건들 일 없음
ROOT_URLCONF = 'DBtest.urls'

# 아직까지 건들 일 없음
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
DATABASES = mysettings.DATABASES

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

FILE_UPLOAD_HANDLERS = [
        "django.core.files.uploadhandler.MemoryFileUploadHandler",
        "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]


# 기타 설정들
LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# static 폴더 경로 지정 및 접근 URL 경로 지정
STATIC_URL = '/static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    STATIC_DIR,
]

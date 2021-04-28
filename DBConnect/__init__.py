# 필요한 모듈 임포트
import os
import uuid
from django.conf.global_settings import FILE_UPLOAD_MAX_MEMORY_SIZE

# 파일 업로드 사이즈 100M ( 100 * 1024 * 1024 )
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600

# 실제 파일을 저장할 경로 및 파일 명 생성
def file_upload_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s"%(uuid.uuid4().hex, ext)
    return os.path.join('static/', filename)

# DB 필드에서 호출
def file_upload_path_for_db(intance, filename):
    return file_upload_path(filename)
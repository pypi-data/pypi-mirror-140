import datetime
import os
from pathlib import Path

from .response import APIResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView


class AiitStorage(FileSystemStorage):

    def url(self, name):
        res = super().url(name=name)
        if res:
            res = '{}?tool={}'.format(res, os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[0])
        return res


def save_request_files(original_files):
    """
    存储文件并返回文件存储路径
    """
    files_new = dict()
    if not Path('media', 'tmp').exists():
        Path('media', 'tmp').mkdir(exist_ok=True)
    for param_name, file_obj in original_files.items():
        file_obj_name = '{}_{}{}'.format(
            Path(file_obj.name).stem,
            datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            Path(file_obj.name).suffix
        )
        file_path = str(Path('media', 'tmp', file_obj_name))
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        files_new[param_name] = '/{}?tool={}'.format(file_path, os.environ.get('DJANGO_SETTINGS_MODULE').split('.')[0])
    return files_new


class FileUploadView(APIView):
    """
    post:

        文件上传接口。在调用算法之前将文件先上传到服务器中。
        可以上传单个或者多个文件，参数名称没有要求。

    """

    def post(self, request):
        files_new = save_request_files(request.FILES)
        return APIResponse(data=files_new)

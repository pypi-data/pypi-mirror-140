from rest_framework.response import Response


class APIResponse(Response):

    def __init__(self, data=None, message='ok', code=200, status=200, headers=None, exception=False, **kwargs):
        # res_data 的初始状态：状态码与状态信息
        res_data = {
            'data': data,
            'message': message,
            'code': code
        }
        res_data.update(kwargs)
        # 重写父类的Response的__init__方法
        super().__init__(data=res_data, status=status, headers=headers, exception=exception)

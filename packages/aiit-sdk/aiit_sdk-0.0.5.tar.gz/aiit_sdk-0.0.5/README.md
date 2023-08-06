# AIIT-SDK

## 安装

```shell
pip install aiit_sdk
```

如果需要指定安装源，可以使用 -i 参数

```shell
pip install aiit-sdk  --index-url https://pypi.org/simple/
```

版本更新，可以使用 --upgrade 参数更新

```shell
pip install --upgrade aiit-sdk  --index-url https://pypi.org/simple/
```

## 使用说明


### 登陆模块

在 settings.py 的 `SIMPLE_JWT.AUTH_TOKEN_CLASSES` 参数下面添加 `aiit_sdk.auth.AiitToken`。

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': (
        'aiit_sdk.auth.AiitToken',  # 允许大数据OS颁发的Token访问
        'rest_framework_simplejwt.tokens.AccessToken',
    ),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=7),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}
```

### 接口返回

```python
from aiit_sdk.response import APIResponse


class FileUploadView(APIView):
    def post(self, request):
        #  业务代码
        data = {}  # 要返回的数据
        return APIResponse(data=data)
```

### 分页模块

#### 默认分页模块的配置

将 settings.py 的 `REST_FRAMEWORK.DEFAULT_PAGINATION_CLASS` 参数设置成 `aiit_sdk.page.NormalResultsSetPagination`。

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
    ),
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DEFAULT_PAGINATION_CLASS': 'aiit_sdk.page.NormalResultsSetPagination',  # 默认分页模块的配置
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter'
    ),
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}
```

### 算法调用模块

通过算法名称调用算法，如果一个算法有多个版本，默认调用最后上传的那个版本。

```python
from aiit_sdk.algo import exec_algo


res = exec_algo(algo_name='cv_name_extra', **params)
```

参数：

- algo_name：算法名称；
- params：调用算法的参数，每个算法有所不同。

### 文件存储

将 settings.py 的 `DEFAULT_FILE_STORAGE` 参数设置成 `aiit_sdk.storage.AiitStorage`。

```python
DEFAULT_FILE_STORAGE = 'aiit_sdk.storage.AiitStorage'
```

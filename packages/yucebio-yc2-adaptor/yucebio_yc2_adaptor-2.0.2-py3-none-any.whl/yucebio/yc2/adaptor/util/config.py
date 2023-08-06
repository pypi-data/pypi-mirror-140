import datetime
import os
import sys, requests
import typing

import jwt

from . import types
from .base_config import Config as BaseConfig
from .ldap import LDAP
from .api import WDLAPI

DEFAULT_PATH = '.yucebioconfig_v2'

class Config(BaseConfig):

    def __init__(self, name: str = 'wdladaptor', path: str = DEFAULT_PATH, check_user: bool = True):
        super().__init__(name=name, path=path)

        self.load()
        # print(self._config)

        if check_user:
            self.check_user()

    @property
    def backends(self) -> typing.List[types.CromwellBackendType]:
        """获取所有可用backend
        """
        backends = self.get('backends')
        if not backends:
            backends = self.init_backends()
        # 检查本地数据是否过期： 每天更新一次
        try:
            update_at = datetime.date.fromisoformat(backends['update_at'])
            if update_at < datetime.date.today() + datetime.timedelta(-1):
                backends = self.init_backends()
        except:
            pass
        return backends['data']

    @property
    def api(self):
        """获取YC-Clou2 API服务器实例
        """
        return WDLAPI(self.get('api', 'http://yc2.yucebio.com'), self.get('owner'))

    def owner(self):
        """获取当前操作人"""
        return self.get('owner', '')

    def set(self, key: str, value):
        self._config[key] = value
        self.reload()

    def get(self, key: str, default = None):
        return self.config.get(key, default)

    def init_backends(self):
        """从API获取数据保存到本地"""
        try:
            backends = self.api.get_backends()
        except:
            return
        saved_backends = {"update_at": datetime.date.today().isoformat(), "data": backends}
        self.set('backends', saved_backends)
        return saved_backends


    def set_api(self, api: str):
        rsp = requests.get(api)
        self.set('api', api)
        return rsp.json()

    def check_user(self):
        """检查用户信息

        1. 检查token是否有效，若token有效，则以token为准
        2. 检查当前登录人是否为ldap有效用户，若是，则自动登录，并更新token
        3. 报错，要求用户登录
        """
        # 1. 检查配置文件中的token是否有效
        user_info = self.check_token()
        if not user_info:
            # 若token无效，基于ldap检查登录用户
            system_username = os.getlogin()
            print("使用当前系统登录用户自动登录", system_username)
            user_info = LDAP().get_user(system_username)
        if not user_info:
            raise RuntimeError("需要登录")
        
        # # 更新过期时间
        user_info = {
            "name": user_info['name'],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        self.set('token', jwt_encode(user_info))
        if self.get('owner') != user_info['name']:
            self.set('owner', user_info['name'])
            self.reload()
        return user_info

    def login(self, username: str, password: str):
        """基于LDAP实现登录"""
        LDAP().check_login(username, password)

        payload = {
            "name": username,
            # 7天内免登录
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        token = jwt_encode(payload)
        self.set('token', token)
        self.reload()
        print(jwt_decode(token))
        return True

    def check_token(self) -> types.UserType:
        """解析jwt-token，提取用户信息

        Args:
            token (str): jwt token
        """
        if not self.get('token'):
            return {}
        try:
            # jwt自带过期时间校验功能
            return jwt_decode(self.get('token'))
        except:
            return {}

    def get_backend_config(self, backend_alias: str):
        """在预设和自定义backend中找到最匹配的
        """
        backends = self.backends
        if not backends:
            raise RuntimeError("无法获取Cromwell backends信息")
        candidate_config = []
        for backend in backends:
            if backend["alias"] == backend_alias:
                if backend["owner"] == self.owner:
                    return backend
                candidate_config.append(backend)
        if not candidate_config:
            raise RuntimeError(f"未找到匹配的Cromwell Backend。（alias=={backend_alias}）")
        return candidate_config[0]


JWT_KWY = DEFAULT_PATH
def jwt_encode(payload: dict, algorithm: str = 'HS256'):
    """基于jwt保存用户信息

    Args:
        payload (dict): 待保存的数据
        key (str): 用于"加密"的辅助信息
    
    Refer to https://pyjwt.readthedocs.io/en/stable/algorithms.html
    """
    return jwt.encode(payload=payload, key=JWT_KWY, algorithm=algorithm)

def jwt_decode(token: str, algorithm: str = 'HS256'):
    return jwt.decode(token, key=JWT_KWY, algorithms=[algorithm])

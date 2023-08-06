import datetime
import ldap3
from functools import lru_cache
import ldap3.core.exceptions
from . import types 

class LDAP(object):

    def __init__(self) -> None:
        super().__init__()

    @lru_cache()
    def get_server(self):

        return ldap3.Server('ldap.yucebio.com')

    def get_connection(self):
        conn = ldap3.Connection(
            server=self.get_server(),
            read_only=True,
            client_strategy=ldap3.SYNC,
            check_names=True,
            raise_exceptions=True
        )
        conn.bind()
        return conn

    # 1. 检查用户是否存在
    def get_user(self, username: str) -> types.UserType:
        connection = self.get_connection() # type: ldap3.Connection
        try:
            connection.search(f'uid={username},ou=People,dc=nodomain', '(objectclass=inetOrgPerson)', attributes=ldap3.ALL_ATTRIBUTES)
        except ldap3.core.exceptions.LDAPNoSuchObjectResult:
            return {}

        data = None
        if len(connection.response) > 0:
            data = connection.response[0]['attributes']
            data['dn'] = connection.response[0]['dn']
        connection.unbind()

        return self.format_from_ldap(data)

    def format_from_ldap(self, ldap_user_info: dict):
        """[summary]

        Args:
            ldap_user_info (dict): [description]
        """
        user_id = ldap_user_info['uid'][0]
        item = {
            "name": user_id,
            # "name_chs": ldap_user_info.get('displayName', user_id),
            # "dingdingId": ldap_user_info.get('pager', [None])[0],
            # "expiry_at": datetime.datetime.now() + datetime.timedelta(days=1),    # 过期时间 24h
        }
        return item

    # 登录并返回当前用户信息
    def check_login(self, username, password):
        conn = ldap3.Connection(
            server=self.get_server(),
            read_only=True,
            user=f'uid={username},OU=People,DC=nodomain',
            password=password,
            client_strategy=ldap3.SYNC,
            check_names=True,
            raise_exceptions=True
        )
        try:
            conn.bind()
        except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
            raise RuntimeError("用户名或密码错误")
        conn.unbind()
import base64
import hmac
import json
import logging
import os
from abc import ABC, abstractmethod

from . import Database, TypeFunc, Hash

zauth_logger = logging.getLogger(__name__)


class SimpleUserPasswdManager:
    def __init__(self, db_file, salt_lenght=64):
        self._salt_lenght = salt_lenght
        try:
            self._db = Database.DB(db_file)
        except KeyError:
            self._db = Database.mkget(db_file)
        self._template = TypeFunc.template.Template(
            username="Unknown",
            hash_type="sha256",
            hash_lenght=64,  # set this param if you use shake_128 or shake_256
            passwd_salt=None,
            passwd_hash=None,
        )
        if not self._db.exist("UserCredentials"):
            self._db.mkmro("UserCredentials", template=self._template)

        self._mrofunc = self._db.getfuncOf("UserCredentials")

    def add(self, username: str, passwd: str, hash_type="sha256", hash_lenght=64):
        if self._mrofunc.exist(username=username):
            raise Database.ExistItemError(username)

        salt = os.urandom(self._salt_lenght)
        passwd_salt = passwd.encode() + salt
        passwd_hash = Hash.getHashValueByName(passwd_salt, hash_type, hash_lenght)

        self._mrofunc.add(
            username=username,
            hash_type=hash_type,
            hash_lenght=hash_lenght,
            passwd_salt=salt,
            passwd_hash=passwd_hash
        )

    def delete(self, username):
        try:
            usr = self._mrofunc.absquery(username=username)
            self._mrofunc.remove(**usr)
        except AssertionError:
            return

    def exist(self, username):
        return self._mrofunc.exist(username=username)

    def query(self, username, passwd):
        try:
            usr = self._mrofunc.absquery(username=username)
            salt = usr["passwd_salt"]
            user_passwd_bytes = passwd.encode()

            true_passwd_hash = usr["passwd_hash"]

            user_passwd_salt = user_passwd_bytes + salt

            if Hash.getHashValueByName(user_passwd_salt, usr["hash_type"], usr["hash_lenght"]) == true_passwd_hash:
                return True
            else:
                return False

        except Database.errors:
            return


# 作为所有Token类的基类

class TokenBase(ABC):
    @abstractmethod
    def serialize(self):
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, *args, **kwargs):
        pass


class JsonWebToken(TokenBase):
    def __init__(self, head: dict, payload: dict, secret_key: str):
        self.head = head
        self.payload = payload
        self.secret = secret_key
        self.signature = self._generate_signature()

        self._head = None
        self._payload = None

    def flush(self):
        header = base64.urlsafe_b64encode(json.dumps(self.head).encode()).decode().rstrip('=')
        payloader = base64.urlsafe_b64encode(json.dumps(self.payload).encode()).decode().rstrip('=')
        self._head, self._payload = header, payloader
        return header, payloader

    def _generate_signature(self):
        # 将头部和负载部分进行 base64url 编码
        # 拼接头部和负载部分
        message = f"{self._head}.{self._payload}".encode()

        # 计算 HMAC-SHA256 签名
        signature = hmac.new(self.secret.encode(), msg=message, digestmod=Hash.hashlib.sha256).digest()

        # 对签名进行 base64url 编码
        return base64.urlsafe_b64encode(signature).decode().rstrip('=')

    def __str__(self):
        self.flush()
        signature = self.signature

        return f"{'.'.join((self._head, self._payload))}.{signature}"

    def serialize(self) -> str:
        self.flush()
        signature = self.signature

        return f"{'.'.join((self._head, self._payload))}.{signature}"

    @classmethod
    def deserialize(cls, secret, token_str: str) -> 'JsonWebToken':
        parts = token_str.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        head = json.loads(base64.urlsafe_b64decode(parts[0] + '==').decode())
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==').decode())
        signature = base64.urlsafe_b64decode(parts[2] + '==')

        # 验证签名
        expected_signature = hmac.new(
            secret.encode(),
            msg=f"{base64.urlsafe_b64encode(json.dumps(head).encode()).decode()}."
                f"{base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()}".encode(),
            digestmod=Hash.hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid signature")

        return cls(head, payload, secret)


class OAuthAccessToken(TokenBase):
    def __init__(self, token: str, expires_in: int, scope: str):
        self.token = token
        self.expires_in = expires_in
        self.scope = scope

    def serialize(self):
        return {
            "token": self.token,
            "expires_in": self.expires_in,
            "scope": self.scope
        }

    @classmethod
    def deserialize(cls, token_str):
        data = json.loads(token_str)
        return cls(data["token"], data["expires_in"], data["scope"])


class RefreshToken(TokenBase):
    def __init__(self, token: str, expires_in: int):
        self.token = token
        self.expires_in = expires_in

    def serialize(self):
        return {
            "token": self.token,
            "expires_in": self.expires_in
        }

    @classmethod
    def deserialize(cls, token_str):
        data = json.loads(token_str)
        return cls(data["token"], data["expires_in"])


class SessionToken(TokenBase):
    def __init__(self, session_id: str, user_id: str, expires_at: int):
        self.session_id = session_id
        self.user_id = user_id
        self.expires_at = expires_at

    def serialize(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "expires_at": self.expires_at
        }

    @classmethod
    def deserialize(cls, token_str):
        data = json.loads(token_str)
        return cls(data["session_id"], data["user_id"], data["expires_at"])


class HashToken(TokenBase):
    def __init__(self, original_token: bytes | None = None, salt: bytes | None = None):
        if original_token is None:
            original_token = os.urandom(32)

        if salt is None:
            salt = os.urandom(16)

        self.original_token = original_token
        self.salt = salt
        self.token = None

    def serialize(self):
        return Hash.getHashValueByName(self.original_token + self.salt, "sha256")

    @classmethod
    def deserialize(cls, *args, **kwargs):
        raise Exception("无法反序列化基于不可逆运算的令牌。")

    def __eq__(self, other: 'HashToken'):
        return self.serialize() == other.serialize()


class HashTokenManager:
    class _HashTokenComparator(HashToken):
        """
        内置的令牌比较器，用于字节串与令牌对象的比较
        """

        def __init__(self, x):
            super().__init__()
            self.token_cmp = x

        def serialize(self):
            return self.token_cmp

        def __eq__(self, other):
            return self.serialize() == other.serialize()

    def __init__(self):
        self._tokens = set()

    def add(self, token: HashToken):
        """
        添加一个令牌对象
        """
        if token in self._tokens:
            raise Exception("Token already exists.")
        else:
            self._tokens.add(token)
            return True

    def add_token(self, original_token: bytes | None = None, salt: bytes | None = None):
        """
        创建一个令牌对象，并添加进内部数据库中
        :param original_token: 原始令牌数据
        :param salt: 随机盐
        """
        obj = HashToken(original_token, salt)
        self.add(obj)
        return obj

    TokenValueType = bytes | HashToken | _HashTokenComparator

    def query(self, token: 'TokenValueType'):
        """
        查询一个令牌
        :param token: 查询的令牌，可以是字节串，令牌对象中的一种
        """
        if isinstance(token, HashToken):
            return token in self._tokens
        if isinstance(token, bytes):
            return self.query(self._HashTokenComparator(token))

    def remove(self, token: 'TokenValueType'):
        """
        删除一个令牌
        :param token: 删除的令牌，可以是字节串、令牌对象中的一种
        """
        if isinstance(token, HashToken):
            if token in self._tokens:
                self._tokens.remove(token)
                return token
            else:
                return False
        if isinstance(token, bytes):
            return self.remove(self._HashTokenComparator(token))


zauth_logger.debug("Module Auth loading ...")

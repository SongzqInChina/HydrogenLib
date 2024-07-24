import logging
import os

from . import zdatabase, typefunc, zhash as shash


zauth_logger = logging.getLogger(__name__)


class SimpleUserPasswdManager:
    def __init__(self, db_file, salt_lenght=64):
        self._salt_lenght = salt_lenght
        try:
            self._db = zdatabase.DB(db_file)
        except KeyError:
            self._db = zdatabase.mkget(db_file)
        self._template = typefunc.template.Template(
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
            raise zdatabase.ExistItemError(username)

        salt = os.urandom(self._salt_lenght)
        passwd_salt = passwd.encode() + salt
        passwd_hash = shash.gethashByName(passwd_salt, hash_type, hash_lenght)

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

            if shash.gethashByName(user_passwd_salt, usr["hash_type"], usr["hash_lenght"]) == true_passwd_hash:
                return True
            else:
                return False

        except zdatabase.errors:
            return


zauth_logger.debug("Module zauth loading ...")

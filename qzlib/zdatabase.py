import fnmatch

from .zfilex import *

zdatabase_logger = logging.getLogger(__name__)


class CannotFindError(BaseException):
    ...


class MultipleTargetItemsError(BaseException):
    ...


class NotExistError(BaseException):
    ...


class ExistItemError(BaseException):
    ...


errors = CannotFindError, MultipleTargetItemsError, NotExistError, ExistItemError


class Template:
    """
    用于设置数据库的数据模版
    """

    def __init__(self, **dic):
        self._template = dic

    @property
    def template(self):
        """
        返回模版字典
        :return:
        """
        return self._template

    @staticmethod
    def instance(tem, dic):
        """
        判断dic是否符合模版tem
        :param tem:
        :param dic:
        :return:
        """
        return (tem.template.keys()) == (dic.keys())

    def instances(self, dic):
        """
        返回dic是否符合模版
        :param dic:
        :return:
        """
        return self.instance(self, dic)


class DB:
    _template = Template()

    def __init__(self, filename):
        assert fnmatch.fnmatch(filename, "*.db"), "文件名必须以.db结尾"
        self._usetype = list
        self._filename = filename
        self._stream = JsonFileOpen(filename)
        self._version = self._stream["version"]
        self._name = self._stream['name']
        self._template = self._stream['template']

        self._stream['data'] = self._stream.get('data', {})
        self._stream.indent = 4

    def mkmro(self, mro, template: Template = _template):
        """
        创建一个数据表
        :param mro:
        :param template:
        :return:
        """
        if mro in self._stream['data']:
            raise KeyError()
        self._stream['data'][mro] = {'data': self._usetype(), 'template': template}

    def clear(self):
        """
        删除所有的表
        :return:
        """
        return self._stream['data'].clear()

    def exist(self, mro):
        """
        如果表mro存在，返回True，否则False
        :param mro:
        :return:
        """
        return mro in self._stream['data']

    def getfuncOf(self, mro):
        """
        返回一个表的操作对象
        :param mro:
        :return:
        """
        return MroFunc(self, mro)

    def mkget(self, mro, template: Template = _template):
        """
        创建一个表并返回它的操作对象
        :param mro:
        :param template:
        :return:
        """
        self.mkmro(mro, template)
        return self.getfuncOf(mro)

    def save(self):
        """
        保存数据库的改动
        :return:
        """
        self._stream.save()

    def __str__(self):
        return f"DB GameObject \n{pickle_free.encode(self._stream['data'])}"

    def __call__(self, _type):
        """
        这个功能用于作为MroFunc的内部接口，请不要随意修改
        :return: Unkown
        """
        if _type == "template":
            return self._template
        if _type == "stream":
            return self._stream
        if _type == "version":
            return self._version
        if _type == "name":
            return self._name


class MroFunc:
    def __init__(self, father: DB, mro):
        self._father = father
        self._mro = mro
        self._stream = self._father("stream")

    @property
    def mro(self):
        return self._mro

    @property
    def father(self):
        return str(self._father)

    @property
    def template(self):
        return self._stream['data'][self.mro]['template']

    def inner(self, dic1: dict, dic2: dict):
        """
        返回dic1是否是dic2的子字典（包括值）
        :param dic1:
        :param dic2:
        :return: bool
        """
        if tuple(dic1.keys()) <= tuple(dic2.keys()):
            for k in dic1:
                if dic1[k] != dic2[k]:
                    return False
            return True
        return False

    def exist(self, **dic):
        return [i for i in self._stream['data'][self.mro]['data'] if self.inner(dic, i)]

    def where(self, **dic):
        """
        找到一个或多个匹配的项，并返回（不存在则返回None）
        :param dic:
        :return:
        """
        ls = []
        for item in self._stream['data'][self.mro]['data']:
            if self.inner(dic, item):
                ls.append(item)
        return ls

    def absquery(self, **dic) -> dict:
        """
        方法要求dic必须有效或是有效数据的一部分，返回唯一的匹配项
        :param dic: 必须有效
        :return:
        """
        ls = self.where(**dic)
        ls_len = len(ls)
        if ls_len < 1:
            zdatabase_logger.debug(f"Error Cannot find item {dic}")
            raise CannotFindError(f"Cannot find item: {dic}")
        if ls_len > 1:
            zdatabase_logger.debug(f"Error Multipie target items: {ls_len}(except 1), query_data={dic}")
            raise MultipleTargetItemsError(f"Multiple target items: {ls_len}(except 1), query_data={dic}")
        return ls[0]

    def remove(self, **dic):
        """
        删除一个有效数据，成功True，失败False
        :param dic:
        :return:
        """
        if not self.exist(**dic):
            zdatabase_logger.debug(f"Dic not exist: {dic}")
            raise NotExistError(f"Not exist: {dic}")
        try:
            data = self.absquery(**dic)
            self._stream['data'][self.mro]['data'].remove(data)
            return True
        except CannotFindError:
            zdatabase_logger.debug(f"Cannot find data {dic}")
            return False
        except MultipleTargetItemsError:
            zdatabase_logger.debug(f"Multiple target items: {dic}")
            return False

    def calibration(self, tem, dic):
        """
        将字典dic转换成完全符合tem的格式
        :param tem:
        :param dic:
        :return:
        """
        for i in tuple(dic):
            if i not in tem.template:
                dic.pop(i)
        for i in tem.template:
            if i not in dic:
                dic[i] = tem.template[i]
        return dic

    def add(self, **dic):
        """
        向表中添加一项数据
        :param dic:
        :return:
        """
        # 检查是否符合模版
        dic = self.calibration(self._stream['data'][self.mro]['template'], dic)
        self._stream['data'][self.mro]['data'].append(dic)

    def format(self):
        """
        对每一个有效数据进行检查并修改（可能会丢失一些数据）
        :return:
        """
        mro = self._stream['data'][self.mro]['data']
        tem = self._stream['data'][self.mro]['template']
        for i in range(len(mro)):
            if not Template.instance(tem, mro[i]):
                mro[i] = self.calibration(tem, mro[i])
        self._stream['data'][self.mro]['data'] = mro

    def settemplate(self, template, update=True):
        """
        设置表数据模版，如果update为True，那么调用format方法更新数据
        :param template:
        :param update:
        :return:
        """
        self._stream['data'][self.mro]['template'] = template
        if update:
            self.format()


def setversion(file, version):
    """
    设置数据库的版本(version)
    :param file:
    :param version:
    :return:
    """
    f = JsonFileOpen(file)
    f['version'] = version
    f.close()


def setname(file, name):
    """
    设置数据的内置名称
    :param file:
    :param name:
    :return:
    """
    f = JsonFileOpen(file)
    f['name'] = name
    f.close()


def settemplate(file, template):
    """
    设置数据库的默认模版
    :param file:
    :param template:
    :return:
    """
    f = JsonFileOpen(file)
    f['template'] = template
    f.close()


def mkdb(file):
    """
    创建/清空一个数据库文件
    :param file:
    :return:
    """
    mkdbEx(file, Template(), 0, "Unkown")


def mkdbEx(file, template, version, name):
    """
    使用更多选项创建数据库
    :param file:
    :param template:
    :param version:
    :param name:
    :return:
    """
    JsonCreate(file)
    setname(file, name)
    settemplate(file, template)
    setversion(file, version)


def mkget(file):
    """
    创建一个数据库并返回它的操作对象
    :param file:
    :return:
    """
    mkdb(file)
    return DB(file)


def mkgetEx(file, template, version, name):
    """
    使用更多选项创建一个数据库并返回它的操作对象
    :param file:
    :param template:
    :param version:
    :param name:
    :return:
    """
    mkdbEx(file, template, version, name)
    return DB(file)


def getdb(file):
    """
    获取一个数据库的操作对象
    :param file:
    :return:
    """
    if not fnmatch.fnmatch(file, "*.db"):
        raise ValueError("数据库文件名必须以.db结尾")
    return DB(file)


def findDB(path):
    """
    查找path内的所有库文件（*.db）
    :param path:
    :return:
    """
    dbs = []
    for i in os.listdir(path):
        if os.path.isfile(i):
            if fnmatch.fnmatch(i, "*.db"):
                dbs.append(i)
    return dbs


def checkDB(file):
    """
    检查文件是否是一个数据库文件
    :param file:
    :return:
    """
    f = JsonFileOpen(file)
    res = set(f.keys()) == {'name', 'version', 'data', 'template'}
    return res


zdatabase_logger.debug(f"Module zdatabase loading ...")

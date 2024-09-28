import pathlib

from ._ConfigLoader import Config


class ConfigCreator:
    def __init__(self, init_path):
        self.path = pathlib.Path(init_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Path {init_path} does not exist")

    def create_config(self, file, name, points):
        """
        创建一个新的配置文件

        :param file: 文件路径
        :param name: 测试名
        :param points: 测试点集合对象
        """
        self._create_config_file(file, name, points)

    def _create_config_file(self, file, name, points):
        c = Config()
        c.name = name
        c.points = points
        c.save(str(self.path / file))

    def del_config(self, file):
        if not (self.path / file).exists():
            raise FileNotFoundError(f"File {file} does not exist")
        (self.path / file).unlink()

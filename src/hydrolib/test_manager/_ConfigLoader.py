from ._BaseStructures import *
from ..json_file import pickle_read, pickle_write


class Config:
    """
    测试配置
    允许读取，保存配置
    属性：
        points: 测试点集合对象
        name: 测试名
        description: 描述
        func: 测试函数
    """
    def __init__(self):
        self.points = Points()
        self.name = None
        self.description = None
        self.func = None

    def run(self):
        return self.points.run(self.func)

    def load(self, file):
        json_config = pickle_read(file)
        points, name, description = json_config.top('points'), json_config.top('name'), json_config.top('description')
        if points is None or name is None or description is None:
            raise ValueError('Invalid config file')
        for p in points:
            self.points.add_point(
                p.top('ext_value'), *p.top('args'), **p.top('kwargs')
            )
        self.name = name
        self.description = description
        return self

    @classmethod
    def load_cls(cls, file):
        return cls().load(file)

    def save(self, file):
        pickle_write(
            {
                'points': [p.to_dict() for p in self.points],
                'name': self.name,
                'description': self.description
            },
            file
        )

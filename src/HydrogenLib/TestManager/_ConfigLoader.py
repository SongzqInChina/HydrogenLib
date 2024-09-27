from ._BaseStructures import *
from ..File import JsonGet, JsonSuSet


class Config:
    def __init__(self):
        self.points = Points()
        self.name = None
        self.description = None
        self.func = None

    def run(self):
        return self.points.run(self.func)

    def load(self, file):
        json_config = JsonGet(file)
        points, name, description = json_config.get('points'), json_config.get('name'), json_config.get('description')
        if points is None or name is None or description is None:
            raise ValueError('Invalid config file')
        for p in points:
            self.points.add_point(
                p.get('ext_value'), *p.get('args'), **p.get('kwargs')
            )
        self.name = name
        self.description = description
        return self

    @classmethod
    def load_cls(cls, file):
        return cls().load(file)

    def save(self, file):
        JsonSuSet(file, **{
            'points': [p.to_dict() for p in self.points],
            'name': self.name,
            'description': self.description
        })

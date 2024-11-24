class Template:
    def __init__(self, **tem):
        self._template = tem

    @property
    def template(self):
        return self._template.copy()


def match(dic, tem):
    from . import Dict as dictx
    if dictx.sub(tem, dic) and dictx.parent(tem, dic):
        return True
    else:
        return False


def sort(dic, tem):
    # 修改字典使字典符合模板
    for i in tem.template:
        if i not in dic:
            dic[i] = tem.template[i]
    return dic


def sub(template: Template, data: dict):
    if data is None:
        return False
    from . import Dict as dictx
    return dictx.sub(template.template, data)

# HydrogenLib

[![PyPI - Version](https://img.shields.io/pypi/v/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)
[![Github Stars](https://img.shields.io/github/stars/SongzqInChina/HydrogenLib.svg)](https://github.com/SongzqInChina/HydrogenLib)

[//]: # ([![Action Status]&#40;https://github.com/SongzqInChina/HydrogenLib/actions/workflows/python-publish.yml/badge.svg&#41;]&#40;)

[//]: # (    https://github.com/SongzqInChina/HydrogenLib/actions&#41;)

---

当前为测试版本,功能可能有**缺失,不完整或错误**,详细请见[注意事项](#注意事项)


## 目录

- [安装](#安装)
- [许可证](#许可证)
- [注意事项](#注意事项)

## 安装

```shell
  pip install HydrogenLib
```

## 注意事项
- 项目的实际开发Python版本为**3.12+**,可能无法运行于低于3.12的Python版本.
- `.Database` 只是一个简单的基于单JSON文件的轻量级数据库，可能不适用于所有使用场景.
- `.Namedpipe` 为非Windows系统的支持未完成.
- `.REPlus` 实现较为简单，可能无法完全满足需求.
- `.HyConfigLanguage` 未完成，且无法使用.
- `.TestManager` 将会在未来版本移除.
- `.Struct`, `.File`等模块整改,相关功能暂时不兼容.
- 对于有关IO功能的函数和类,大多使用了异步模式，请注意兼容性.

- 代码实现中有关序列化和反序列化的操作，均使用`jsonpickle`模块，可能有安全风险.
- **所有模块均未进行测试.**

## 许可证

项目使用[`HydrogenLib License`](License.md)许可证.

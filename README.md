# HydrogenLib

[![PyPI - Version](https://img.shields.io/pypi/v/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)
[![Github Stars](https://img.shields.io/github/stars/SongzqInChina/HydrogenLib.svg)](https://github.com/SongzqInChina/HydrogenLib)

## 当前为测试版本，功能不完整，详细请见 [注意事项](#注意事项)

-----


## 目录

- [安装](#安装)
- [许可证](#许可证)
- [注意事项](#注意事项)

## 安装

```console
pip install HydrogenLib
```

## 注意事项

- 模块标注的是Python版本需大于`1.12.0`，实际可能允许运行在`1.12.0`以下版本（可能的最低版本`Python3.7`）。 
- `.Database` 只是一个简单的基于单JSON文件的轻量级数据库，可能不适用于所有使用场景。
- `.Namedpipe` 为非Windows系统的支持未完成。
- `.REPlus` 实现较为简单，可能无法完全满足需求。
- `.InteractiveCLI` 子模块暂时停止开发。
- `.HyConfigLanguage` 未完成，且无法使用
- `.TestManager` 将会在未来版本移除，改用将要开发的`HyTest`。
- 对于有关IO功能的函数和类，大多使用了异步模式，请注意兼容性。

- 代码实现中有关序列化和反序列化的操作，均使用`jsonpickle`模块，可能有安全风险。
- **所有模块都未进行测试。**


## 许可证

`HydrogenLib` 使用 [GPL](https://spdx.org/licenses/GPL-3.0.html)许可证([Open LICENSE.md](LICENSE.md)).

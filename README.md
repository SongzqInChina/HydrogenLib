# HydrogenLib

[![PyPI - Version](https://img.shields.io/pypi/v/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hydrogenlib.svg)](https://pypi.org/project/hydrogenlib)

-----

**您当前使用的版本为`1.1.25` （低于 `1.2.0` ）开发版本，可能有部分功能未完成或功能异常**

## 目录

- [为什么这个项目被称为 `HydrogenLib`?](#为什么这个项目被称为-hydrogenlib)
- [安装](#安装)
- [许可证](#许可证)
- [注意事项](#注意事项)

## 安装

```console
pip install HydrogenLib
```
## 为什么这个项目被称为 `HydrogenLib`?

Hydrogen(氢)是元素周期表中的第一个元素，是所有元素中最轻的元素。
这个项目希望为底层的低级操作封装，以方便开发者使用，简化编码。

## 注意事项

- `HydrogenLib.Database` 只是一个简单的基于JSON文件的轻量级数据库，可能不适用于所有使用场景。
- `HydrogenLib.BoardcastRoom` 未完成。
- `HydrogenLib.Namedpipe` 为非Windows系统的支持未完成。

- 有关序列化和反序列化的操作，均使用`jsonpickle`模块，可能有安全风险，请自行判断。
- ### 所有模块都未进行测试。


## 许可证

`HydrogenLib` 使用 [GPL](https://spdx.org/licenses/GPL-3.0.html)许可证([Open LICENSE.md](LICENSE.md)).

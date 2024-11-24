from . import __error_hook, __about__

init = __error_hook.init

__version__ = __about__.__version__

# TODO: 由于Socket模块的API更改, 需要修改所有使用Socket的代码
# TODO: Struct模块整改,未完成
# TODO: 解决下载器的Task响应问题
# TODO: HyConfigLanguager未完成

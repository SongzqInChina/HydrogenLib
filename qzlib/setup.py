from setuptools import setup, find_packages

setup(
   name='your_package_name',
   version='0.1',
   packages=find_packages(),
   install_requires=[
       'copy',
       'struct',
       'rsa',
       'logging',
       'pyaes',
       'jsonpickle',
       'fnmatch',
       'hashlib',
       'pywin32',
       'importlib',
       'inspect',
       'msvert',
       'psutil',
       'winreg',
       'argparse',
       # 列出你的所有依赖项
   ],
   entry_points={
       'console_scripts': [
           'command_name = your_package_name.module:function',
           # 格式为 '命令名=模块名:函数名'
       ],
   },
   # 可以添加更多元数据如author, author_email, description等
)

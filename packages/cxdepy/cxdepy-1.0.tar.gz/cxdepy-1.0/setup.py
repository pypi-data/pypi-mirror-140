
from distutils.core import setup

setup(
    name='cxdepy', # 对外我们模块的名字
    version='1.0', # 版本号
    description='这是第一个对外发布的模块', #描述
    author='cx', # 作者
    author_email='404431634@qq.com',
    py_modules=['cxdepy.demo1','cxdepy.demo2'] # 要发布的模块
)
# -- coding: utf-8 --
# @Time : 2021/12/13 9:58
# @Author : 怃
# @Email : chenzhe12320@163.com
# @File : setup.py.py
# @Project : tztHytest
# @Description : xxx
from setuptools import find_packages, setup
from os.path import join

from tztHytest.product import version

CLASSIFIERS = """
Development Status :: 4 - Beta
Intended Audience :: Developers
Topic :: Software Development :: Testing
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
""".strip().splitlines()

with open('README.md', encoding='utf8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='tztHytest',
    version=version,
    author='cz',
    author_email='1781311641@qq.com',
    license='Apache License 2.0',
    description='一款系统测试自动化框架 Generic automation framework for QA testing,修改自hytest',
    keywords='tztHytest automation testautomation',
    classifiers=CLASSIFIERS,

    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    #   find_packages() 会从setup.py 所在的目录下面寻找所有 认为有效的python  package目录
    #   然后拷贝加入所有相关的 python 模块文件，但是不包括其他类型的文件
    # packages     = find_packages(),
    packages=find_packages(
        include=['tztHytest', 'tztHytest.*']
    ),

    # 参考  https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
    # https://docs.python.org/3/distutils/setupscript.html#installing-package-data
    #  其他类型的文件， 必须在 package_data 里面指定 package目录 和文件类型,
    #  这里 package目录为空，我猜是表示 所有的package 里面包含 .css 和 .js 都要带上
    package_data={'': ['*.css', '*.js']},

    install_requires=[
        'rich',
        'dominate'
    ],
    entry_points={
        'console_scripts':
            [
                'tztHytest = tztHytest.run:run',
            ]
    }
)

'''
name : 打包后包的文件名
version : 版本号
author : 作者
author_email : 作者的邮箱
py_modules : 要打包的.py文件
packages: 打包的python文件夹
include_package_data : 项目里会有一些非py文件,比如html和js等,这时候就要靠include_package_data 和 package_data 来指定了。
                        package_data:一般写成{‘your_package_name’: [“files”]}, include_package_data还没完,
                        还需要修改MANIFEST.in文件.MANIFEST.in文件的语法为: include xxx/xxx/xxx/.ini/(所有以.ini结尾的文件,
                        也可以直接指定文件名)
license : 支持的开源协议
description : 对项目简短的一个形容
ext_modules : 是一个包含Extension实例的列表,Extension的定义也有一些参数。
ext_package : 定义extension的相对路径
requires : 定义依赖哪些模块
provides : 定义可以为哪些模块提供依赖
data_files :指定其他的一些文件(如配置文件),规定了哪些文件被安装到哪些目录中。如果目录名是相对路径,则是相对于sys.prefix
            或sys.exec_prefix的路径。如果没有提供模板,会被添加到MANIFEST文件中。
'''
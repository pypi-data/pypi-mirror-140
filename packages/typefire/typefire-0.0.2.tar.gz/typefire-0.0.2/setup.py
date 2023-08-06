from distutils.core import setup
from setuptools import find_packages

setup(name='typefire',  # 包名
      version='0.0.2',  # 版本号
      description='基于类型注解的自定义类型转换, 可用于拓展 fire 解析类型',
      long_description='https://github.com/luxuncang/typefire',
      author='ShengXin Lu',
      author_email='luxuncang@qq.com',
      url='https://github.com/luxuncang/typefire',
      install_requires=['SimilarNeuron', 'fire'],
      license='MIT',
      packages=find_packages(),
      include_package_data = True,
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries'
      ],
      )
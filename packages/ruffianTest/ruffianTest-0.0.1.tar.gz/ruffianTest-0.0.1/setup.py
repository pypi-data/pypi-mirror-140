from distutils.core import setup
from setuptools import find_packages

with open("README.md", 'rb') as f:
    long_description = f.read()

setup(name='ruffianTest',  # 你包的名称
      version='0.0.1',  # 版本号
      description='test',  # 描述
      long_description=long_description,  # 长描述
      long_description_content_type='text/markdown',
      author='The-Ruffian',
      author_email='',
      url='https://github.com/the-ruffian/ruffian_test',
      download_url='https://github.com/the-ruffian/ruffian_test',
      install_requires=['PyMySQL'],  # 依赖第三方库
      license='MIT License',
      keywords=['bug_pz', 'the-ruffian', 'ruffianTest', 'ruffian', 'test'],
      packages=find_packages(),
      platforms=['all'],  # 平台
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Testing',
          'Development Status :: 5 - Production/Stable'
      ],
      )

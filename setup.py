from setuptools import setup, find_packages

setup(name='mercury-base',
      version='1.3',
      url='https://github.com/webtoucher/mercury-base',
      license='BSD-3-Clause',
      author='Alexey Kuznetsov',
      author_email='mirakuru@webtoucher.ru',
      description='Toolkit for communicating with Incotex Mercury meters via RS485/CAN bus',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Terminals :: Serial',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Operating System :: Unix',
      ],
      packages=find_packages(),
      long_description=open('README.md', encoding='utf-8').read(),
      long_description_content_type='text/markdown',
      install_requires=[
          'modbus-crc~=1.3',
          'pyserial~=3.0',
          'simple-socket-client~=1.4',
      ],
      zip_safe=False)

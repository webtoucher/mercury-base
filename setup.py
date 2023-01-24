from setuptools import setup

setup(name='mercury-base',
      version='1.0',
      url='https://github.com/webtoucher/mercury-base',
      license='BSD-3-Clause',
      author='Alexey Kuznetsov',
      author_email='mirakuru@webtoucher.ru',
      description='Toolkit for communicating with Incotex Mercury meters via RS485/CAN bus',
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'Topic :: Terminal :: Serial',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Operating System :: Unix',
      ],
      packages=['mercury_base'],
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      zip_safe=False)

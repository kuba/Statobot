from setuptools import setup, find_packages
import sys, os

version = '0.1dev'

setup(name='Statobot',
      version=version,
      description="Stat bot for moniotring servers.",
      keywords='bot stats unix',

      author='Jakub Warmuz',
      author_email='jakub.warmuz@gmail.com',

      packages=find_packages(),
      data_files = [('twisted/plugins', ['twisted/plugins/statobot_plugin.py'])],
      include_package_data=True,
      install_requires=['Twisted>=8.2.0', 'PrettyTimedelta>=0.1dev'],
      )

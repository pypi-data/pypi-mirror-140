from setuptools import setup, find_packages


setup(
    name='pirtul',
    version='1.0.1',
    license='MIT',
    author="Akimbo",
    author_email='akimbo7@protonmail.com',
    description='A simple API Wrapper for Norton Hill Portal.',
    packages=find_packages(),
    url='https://github.com/akimbo7/Pirtul',
    install_requires=[
          'requests',
          'bs4',
          'lxml',
      ],

)

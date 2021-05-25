from setuptools import setup, find_packages
setup(name='shepherd', 
      version='1.0',
      packages=find_packages()
      install_requires=[
        'Flask',
        'Flask-SocketIO',
        'google-api-python-client'
      ])


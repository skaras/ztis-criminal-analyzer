try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

config = {
    'name': 'ztis',
    'description': 'ztis',
    'version': '0.1',
    'install_requires': ['SQLAlchemy'],
    'packages': find_packages()
}

setup(**config)

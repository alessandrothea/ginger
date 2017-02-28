try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Alessandro Thea',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'timelike@gmail.com.',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['ginger'],
    'scripts': [],
    'name': 'ginger'
}

setup(**config)

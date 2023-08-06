from setuptools import setup, find_packages
from wai.version import author, version, homepage

with open("README.md", 'r') as f:
  long_description = f.read()

setup(
  author=author,
  author_email='dlek@p0nk.net',
  url=homepage,
  project_urls={
    'Source': 'https://gitlab.com/dlek/wai-client',
    'Tracker': 'https://gitlab.com/dlek/wai-client/issues'
  },
  python_requires='>=3.6',
  description='Wai client app',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  install_requires=['requests', 'toga>=v0.3.0dev32', 'emoji'],
  license="MIT license",
  include_package_data=True,
  name='wai-client',
  packages=['wai'],
  version=version,
  entry_points = {
    'console_scripts': [
      'wai = wai.__main__:run',
    ],
  }
)

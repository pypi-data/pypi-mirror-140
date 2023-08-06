from setuptools import setup, Extension
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'easypype',         # How you named your package folder (MyLib)
  packages = ['easypype'],   # Chose the same as "name"
  version = '1.1.2',      # Start with a small number and increase it with every change you make
  license='unlicense',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Easy way of creating pipelines',   # Give a short description about your library
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  author = 'Gabriel Felix de Souza Lopes <gafelix435@gmail.com>, Alejandro Tarafa Guzmán <alejandro.guzman@looplex.com.br>',                   # Type in your name
  url = 'https://github.com/looplex/easypype/tree/main',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/looplex/easypype/archive/refs/tags/v1.1.2.tar.gz',    # I explain this later on
  keywords = ['Pipeline', 'ETL', 'transform', 'load', 'pipe'],   # Keywords that define your package best
  install_requires = [            # I get to this in a second
      ],
  classifiers = [
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
  python_requires = '>=3.5',
)

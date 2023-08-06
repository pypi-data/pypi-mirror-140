from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pyalvarockcl',
      version='1.26',
      description='version 1.26',
      url='https://github.com/DataBeamCL/pyalvarockcl',
      author='Alvaro Fuentes',
      author_email='alvarofue@gmail.com',
      license='Apache 2.0',
      packages=['pyalvarockcl'],
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown',
      keywords='test lib',
      classifiers=sorted([
            'Programming Language :: Python :: 3.10',
      ]),    
)
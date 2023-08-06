from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(name='pyalvarockcl',
      version='1.22',
      description='version 1.22',
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
            'Development Status :: 1 - Planning',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',            
            'Programming Language :: Python :: 3.10',
      ]),
      install_requires=[],    
)
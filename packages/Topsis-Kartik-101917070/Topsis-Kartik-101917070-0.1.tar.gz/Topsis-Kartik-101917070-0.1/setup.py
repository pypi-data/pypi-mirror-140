import pathlib
from setuptools import setup
from distutils.core import setup
HERE = pathlib.Path(__file__).parent
setup(
  name = 'Topsis-Kartik-101917070',         
  packages = ['Topsis-Kartik-101917070'],   
  version = '0.1',      
  license='MIT',       
  description = 'Kartik Arora 101917070 cse-3 topsis assignment-4',   
  author = 'Kartik Arora',                   
  author_email = 'karora_be19@thapar.edu',      
  url = 'https://github.com/kartikarora8/Topsis-Kartik-101917070',   
  download_url = 'https://github.com/kartikarora8/Topsis-Kartik-101917070/archive/v_01.tar.gz',   
  keywords = ['numpy', 'pandas', 'eucledian'],   
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',     
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
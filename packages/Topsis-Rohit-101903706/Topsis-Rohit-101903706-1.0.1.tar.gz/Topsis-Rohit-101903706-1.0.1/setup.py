from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent

VERSION = '1.0.1'
DESCRIPTION = 'Topsis Package'
LONG_DESCRIPTION = (this_directory /"README.md").read_text()

# Setting up
setup(
    name="Topsis-Rohit-101903706",
    version=VERSION,
    author="Rohit Jain",
    author_email="<rjain1_be19@thapar.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    setup_requires=['wheel'],
    install_requires=['numpy', 'pandas'],
    keywords=['python', 'topsis', 'thapar', 'Prdictive-Analysis', '101903706'],
    classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Developers',   
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',  
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  entry_points={
    "console_scripts":[
      "topsis=topsis.topsis:topsis",
    ]
  },
)
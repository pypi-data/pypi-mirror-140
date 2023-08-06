import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

VERSION = '0.0.2'
DESCRIPTION = 'Topsis Package'
LONG_DESCRIPTION = 'A package as part of Predictive Analysis course at Thapar Institute of Engineering'

# Setting up
setup(
    name="Topsis-Tarush-102083060",
    version=VERSION,
    author="Tarush Srivastava",
    author_email="<tarush33@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=README,
    packages=find_packages(),
    setup_requires=['wheel'],
    install_requires=['numpy', 'pandas'],
    keywords=['python', 'topsis', 'thapar', 'Prdictive-Analysis', '102083060'],
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
      "topsis=topsis.topsis:main",
    ]
  },
)
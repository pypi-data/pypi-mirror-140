from setuptools import setup, find_packages
import os


VERSION = '1.0.4'
DESCRIPTION = 'Alpha Numeric Cipher aka ancihper'
LONG_DESCRIPTION = '''
# **Ancipher**
**"Alpha Numeric Cipher"**

<br> 

### 🪛 Installtion

It is a python (precisely v3) package, uploaded on [PyPi](https://pypi.org/project/ancipher/).

```
pip install ancipher
```

<br> 

### 📑 Usage
Firstly import it:  
```
from ancipher import anc
```
Now, use `anc()` (datatype: string)
```
anc("As simple as that!")
```
Output
```
45 51mpl3 45 7h47!
```

<br> 

### 🖱️ Requirements
Obviously ***Python 3***

<br><br>

> A Divinemonk creation!
'''


# Setting up
setup(
    name="ancipher",
    version=VERSION,
    author="Divinemonk",
    author_email="<v1b7rc8eb@relay.firefox.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url = 'https://github.com/Divinemonk/ancipher/',
    packages=['ancipher'],
    #py_modules = [],
    #install_requires=[''],
    keywords=['python', 'python3', 'cipher', 'ancipher'],
    entry_points={
        "console_scripts": [
          "ancipher=ancipher.__main__:console_script"
        ]},
    # include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License"
    ]
)
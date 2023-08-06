# generic-web-server
Generic Web Server.
## Getting Started
#### Dependencies
You need Python 3.7 or later to use **generic-web-server**. You can find it at [python.org](https://www.python.org/).
You also need setuptools, wheel and twine packages, which is available from [PyPI](https://pypi.org). If you have pip, just run:
```
pip install setuptools
pip install wheel
pip install twine
```
#### Installation
Clone this repo to your local machine using:
```
git clone https://github.com/matheusphalves/generic-web-server
```
#### How to run

Basically, you need to import the Server class and execute the method `run`. 
```
from Server import Server

server_instance = Server()
server_instance.run()
```

## Features
- File structure for PyPI packages
- Setup with package informations
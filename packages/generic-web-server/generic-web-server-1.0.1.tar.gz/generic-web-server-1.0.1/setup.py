from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(name='generic-web-server',
    version='1.0.1',
    url='https://github.com/matheusphalves/generic-web-server',
    license='MIT License',
    author= ['Matheus Phelipe','Murilo Stodolni', 'Nilton Vieira',  'Richard Jeremias'],
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='matheusphalves@gmail.com',
    keywords=['Package', 'HTTP', 'Network', 'Sockets'],
    description=u'Basic generic web server application developed for HTTP protocol studies under networking purposes',
    packages=['generic-web-server'],
    install_requires=['termcolor'],)
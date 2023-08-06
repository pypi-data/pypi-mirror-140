from email.mime import audio
from setuptools import setup, find_packages

classifers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
]

setup(
    name='colereader',
    version='0.0.1',
    description='This python module replaces, writes and clears text files making it much quicker then writing it out the normal way.',
    long_description=open("README.txt").read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Cole',
    author_email='Coleberr1@gmail.com',
    license='MIT',
    classifiers=classifers,
    keywords='',
    packages=find_packages(),
    install_requires=[''],
)
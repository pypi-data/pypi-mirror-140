from setuptools import *
from pathlib import Path

directory = Path(__file__).parent
longDescription = (directory/'README.md').read_text()

setup(
    name='termclock',
    version='1.1.0',
    packages=['clock'],
    install_requires=['click'],
    long_description=longDescription,
    long_description_content_type='text/markdown',
    author='Cargo',
    entry_points='''
    [console_scripts]
    cdate=clock:cdate
    ctime=clock:ctime
    cdatetime=clock:cdatetime
    '''
)
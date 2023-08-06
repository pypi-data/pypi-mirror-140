from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='asyncio_tcp_messages_team_2',
    version='0.1.0',
    packages=['tests', 'asyncio_tcp_messages_team_2'],
    url='https://gitlab.com/python-2k2s-2022/asyncio-tasks-submissions/team-2',
    license='WTFPL',
    author='narut',
    author_email='naruto.shipudet@mail.ru',
    description='asynchronous joke'
)

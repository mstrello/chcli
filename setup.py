from setuptools import setup

setup(
    name='chcli',
    version='0.1',
    py_modules=['chcli'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        chcli=chcli:cli
    ''',
)
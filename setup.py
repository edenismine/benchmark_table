from setuptools import setup

setup(
    name='table',
    version='1.0',
    py_modules=['table'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        table=table:cli
    ''',
)

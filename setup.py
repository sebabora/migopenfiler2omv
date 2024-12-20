from setuptools import setup

setup(
        name = 'cli',
        version = '0.1.0',
        py_modules=['cli']
        install_requires=[
            'Click',
            'ldif',
            'rich',
        ],
        entry_points={
            'console_scripts': [
            'migrationscript = migrationscript:cli',
        ],
)
                

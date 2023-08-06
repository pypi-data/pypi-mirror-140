from setuptools import setup, find_packages

setup(
    name='MRSQL',
    version='0.0.2',
    license='MIT',
    author="Manuel Raffl",
    author_email='manuraffl003@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/manuraffl30/SimpleMySQL',
    keywords='MRSQL',
    install_requires=['mysql-connector-python',],
)
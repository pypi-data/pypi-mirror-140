from setuptools import find_packages, setup

setup(
    name='diamond_registry',
    packages=find_packages(include=['diamond_registry']),
    install_requires=['mysql-connector-python'],
    version='0.0.1',
    author='Louise Poole',
    author_email='louisecarmenpoole@gmail.com',
    description='Diamond registry and price estimation system',
    url='https://gitlab.com/data-revenue/code-challenge/submissions/diamonds-louise',
    license='MIT'
)
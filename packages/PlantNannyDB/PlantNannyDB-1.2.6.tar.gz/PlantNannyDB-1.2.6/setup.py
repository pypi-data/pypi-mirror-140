from setuptools import setup, find_packages

try:
    with open('README.md') as f:
        readme = f.read()
except:
    pass

try:
    with open('LICENSE.txt') as f:
        license = f.read()
except:
    pass

setup(
    name='PlantNannyDB',
    version='1.2.6',
    description='Enable read/write functionality for Plant Nanny Database',
    long_description='readme.md',
    long_description_content_type = 'text/markdown',
    author='Logan Balkwill',
    author_email='lgb0020@gmail.com',
    url='https://github.com/loganbalkwill/plant-nanny-db',
    license='LICENSE.txt',
    packages=find_packages(exclude=('tests', 'sensors')),
    include_package_data = True,
    install_requires = ["mysqlclient", "importlib"]
)
from setuptools import setup, find_packages

setup(name='pwt',
      packages=find_packages(exclude=['tests*']),
      version='0.1.0',
      description='Python package for generating the Penn World Tables data set.',
      author='David R. Pugh',
      author_email='david.pugh@maths.ox.ac.uk',
      url='https://github.com/davidrpugh/penn-world-tables',
      license='LICENSE.txt',
      install_requires=['pandas'],
      )

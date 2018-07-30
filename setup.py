import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='sugarcrm-python',
      version='0.1.3',
      description='API wrapper for SugarCRM written in Python',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      url='https://github.com/GearPlug/sugarcrm-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='GPL',
      packages=['sugarcrm'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)

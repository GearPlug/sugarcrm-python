from setuptools import setup

setup(name='sugarcrm',
      version='0.1',
      description='API wrapper for SugarCRM written in Python',
      url='https://github.com/GearPlug/sugarcrm-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='GPL',
      packages=['sugarcrm'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)

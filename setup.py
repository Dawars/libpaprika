from setuptools import setup

setup(name='libpaprika',
      version='0.1',
      description='Simple headless rendering library that renders model from an OBJ like format',
      url='http://github.com/dawars/libpaprika',
      author='Dawars',
      author_email='dawars00@gmail.com',
      license='',
      packages=['libpaprika'],
      zip_safe=False,
      install_requires=[
          'moderngl', 'Pillow'
      ],
      )

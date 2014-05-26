"""
PHPLY
--------------------
PHP lexer and parser in Python
"""
from setuptools import setup, find_packages

setup(name="phply",
      version="0.9.1",
      packages=find_packages(),
      namespace_packages=['phply'],
      include_package_data=True,
      author='Ramen',
      author_email='',
      description='PHP lexer and parser in Python',
      long_description=__doc__,
      zip_safe=False,
      platforms='any',
      license='BSD',
      url='http://www.github.com/ramen/phply',

      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: PHP',
        'Operating System :: Unix',
        ],

      # entry_points={
      #   'console_scripts': [
      #       ],
      #   },

      install_requires=[
        'ply',
        ],

      test_suite='nose.collector',
      tests_require=[
        'nose',
        ],
      )

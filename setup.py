"""
PHPLY
--------------------
PHP implemented in Python
"""
from setuptools import setup, find_packages

setup(name="phply",
      version="dev",
      packages=find_packages(),
      namespace_packages=['phply'],
      include_package_data=True,
      author='Ramen',
      author_email='',
      description='PHP in Python',
      long_description=__doc__,
      zip_safe=False,
      platforms='any',
      license='BSD',
      url='https://github.com/viraptor/phply',

      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: PHP',
        'Operating System :: Unix',
        ],

      entry_points={
        'console_scripts': [
            'phpparse=phply.phpparse:run_on_stdin',
            'phplex=phply.phplex:run_on_argv1',
            ],
        },

      install_requires=[
        'ply',
        'wheel',
        ],

      test_suite='nose.collector',
      tests_require=[
        'nose',
        ],
      )

# coding: utf-8
from __future__ import unicode_literals

from setuptools import setup, find_packages, Command
from distutils.command.build import build as distutils_build

distutils_build.sub_commands.insert(0, ('gen_parsetab', lambda _: True))


class GenerateParsetab(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from phply.phpparse import make_parser
        make_parser(debug=False)


setup(name="phply",
      version="1.2.4",
      packages=find_packages(),
      namespace_packages=['phply'],
      include_package_data=True,
      author='Ramen',
      author_email='',
      maintainer='Stanisław Pitucha',
      maintainer_email='viraptor@gmail.com',
      description='Lexer and parser for PHP source implemented using PLY',
      zip_safe=False,
      platforms='any',
      license='BSD',
      url='https://github.com/viraptor/phply',

      classifiers=[
        'Development Status :: 5 - Production/Stable',
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
            'phpparse=phply.phpparse:main',
            'phplex=phply.phplex:run_on_argv1',
            ],
        },

      install_requires=[
        'ply',
        ],
      setup_requires=[
        'ply',
        ],

      test_suite='nose.collector',
      tests_require=[
        'nose',
        ],

      cmdclass={
          'gen_parsetab': GenerateParsetab,
          }
      )

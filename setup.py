from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='pastebiner',
      version='0.1',
      description='Python wrapper for pastebin',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules'
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='pastebin paste code text api',
      url='http://github.com/vThaian/pastebin-python',
      author='Bartosz Plociennik',
      author_email='bartosz@plociennik.net',
      license='Apache 2.0',
      packages=['pastebiner'],
      install_requires=[
          'requests',
          'xmltodict'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False,
      include_package_data=True)

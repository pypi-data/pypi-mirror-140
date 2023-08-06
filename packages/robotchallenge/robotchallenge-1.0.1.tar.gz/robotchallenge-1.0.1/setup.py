from setuptools import setup, find_packages


setup(
    name='robotchallenge',
    version='1.0.1',
    license='Apache 2.0',
    author="Sheece Gardezi",
    author_email='sheecegardezi@gmail.com',
    packages=find_packages('robotchallenge'),
    package_dir={'': 'robotchallenge'},
    url='https://github.com/sheecegardezi/RobotChallenge',
    keywords='robot challenge',
    install_requires=[
          'pytest',
      ],
    python_requires='>=3.7',
)

from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='PySortedSet',
    version='1.2',
    packages=['PySortedSet'],
    url='https://github.com/DigitalCreativeApkDev/PySortedSet',
    license='MIT',
    author='DigitalCreativeApkDev',
    author_email='digitalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the library "PySortedSet". PySortedSet is a data type '
                'supporting a sorted set which is aware of indices.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7"
    ],
    entry_points={
        "console_scripts": [
            "PySortedSet=PySortedSet.PySortedSet_versus_set:main",
        ]
    }
)
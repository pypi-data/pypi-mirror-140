from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='ObjectAsString',
    version='1',
    packages=['ObjectAsString'],
    url='https://github.com/DigitalCreativeApkDev/ObjectAsString',
    license='MIT',
    author='DigitalCreativeApkDev',
    author_email='digitalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the library "ObjectAsString". ObjectAsString is a library '
                'which makes coding in Python feel like Java and JavaScript. "+" operator will automatically be '
                'string concatenation if non-numeric types are involved.',
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
            "ObjectAsString=ObjectAsString.ObjectAsString_versus_string:main",
        ]
    }
)
from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='StaticTypedList',
    version='1',
    packages=['StaticTypedList'],
    url='https://github.com/DigitalCreativeApkDev/StaticTypedList',
    license='MIT',
    author='DigitalCreativeApkDev',
    author_email='digitalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the library "StaticTypedList". StaticTypedList is a data type '
                'supporting a list of one type of element (and its subtypes) like Java List objects.',
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
            "StaticTypedList=StaticTypedList.StaticTypedList_versus_list:main",
        ]
    }
)
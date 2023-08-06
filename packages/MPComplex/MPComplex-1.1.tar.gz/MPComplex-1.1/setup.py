from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='MPComplex',
    version='1.1',
    packages=['MPComplex'],
    url='https://github.com/DigitalCreativeApkDev/MPComplex',
    license='MIT',
    author='DigitalCreativeApkDev',
    author_email='digitalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the library "MPComplex". MPComplex is a data type '
                'supporting complex numbers which allow comparison and sorting operations.',
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
            "MPComplex=MPComplex.mp_complex_versus_mpc:main",
        ]
    }
)
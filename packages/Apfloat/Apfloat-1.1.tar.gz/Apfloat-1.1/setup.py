from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='Apfloat',
    version='1.1',
    packages=['Apfloat'],
    url='https://github.com/DigitalCreativeApkDev/Apfloat',
    license='MIT',
    author='DigitalCreativeApkDev',
    author_email='digitalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the library "Apfloat". Apfloat is a data type '
                'supporting arbitrary-precision numbers.',
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
            "Apfloat=Apfloat.apfloat_versus_mpf:main",
        ]
    }
)
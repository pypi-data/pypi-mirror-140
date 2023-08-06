from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_101903570",
    version="4.1.0",
    description="Python package to implement TOPSIS",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/saksham02112000/topsis-101903570",
    author="Saksham",
    author_email="sakshamsrini@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101903570"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "topsis-101903570=topsis_101903570.__init__:main",
        ]
    },
)

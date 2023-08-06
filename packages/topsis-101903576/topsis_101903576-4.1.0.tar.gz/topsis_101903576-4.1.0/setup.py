from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_101903576",
    version="4.1.0",
    description="Python package to implement TOPSIS",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ABHISHEK-WD-13/topsis-101903576",
    author="Abhishek",
    author_email="abhi013lamba@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_101903576"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "topsis-101903576=topsis_101903576.__init__:main",
        ]
    },
)

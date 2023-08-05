from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Topsis-Shubham-101903131",
    version="1.1.2",
    description="A Python package implementing TOPSIS technique.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Shubham Trivedi",
    author_email="strivedi_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_py"],
    include_package_data=True,
    install_requires=['numpy',
                      'pandas'
                      ],
    entry_points={
        "console_scripts": [
            "topsis=topsis_py.topsis:main",
        ]
    },
)

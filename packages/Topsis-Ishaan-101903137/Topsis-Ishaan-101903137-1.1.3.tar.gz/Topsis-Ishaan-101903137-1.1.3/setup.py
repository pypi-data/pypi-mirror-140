from setuptools import setup


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Topsis-Ishaan-101903137",
    version="1.1.3",
    description="A Python package implementing TOPSIS technique.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Ishaan Bajaj",
    author_email="ibajaj1_be19@thapar.edu",
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

from setuptools import setup, find_packages

VERSION = '0.1.7'
DESCRIPTION = 'Notion API implementation for Python'

with open('README.md', 'r') as readme:
    LONG_DESCRIPTION = readme.read();

setup(
    name="notyon",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="guilhermigg",
    author_email="guilhermigg@protonmail.com",
    url="https://gitlab.com/guilhermigg/notyon",
    download_url="https://gitlab.com/guilhermigg/notyon",
    license='MIT',
    packages=find_packages(),
    install_requires = ["requests"],
    extras_require={
        "dev": [
            "pytest>=3.7",
        ]
    },
    keywords=['notion', 'api', 'notyon', 'sdk', 'Notion API', 'notionsdk'],
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ]
)

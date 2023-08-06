from setuptools import setup, find_packages

def readme():
    with open('readme.txt') as f:
        README = f.read()
    return README

setup(
    name = "Topsis-AnanyaAga-102083036",
    version = "0.5.3",
    license = "MIT",
    description = "A Python package to find TOPSIS for multi-criteria decision analysis method",
    long_description = readme(),
    long_description_content_type = "text/markdown",
    author = "Ananya Agarwal",
    author_email = "aagarwal3_be19@thapar.edu",
    install_requires = ['pandas', 'tabulate'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3' 
    ]
)

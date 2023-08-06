from setuptools import setup, find_packages

setup(
    name = "Topsis-Soumil-101903663",
    version = "0.0.1",
    license = "MIT",
    description = "A Python package to find TOPSIS for multi-criteria decision analysis method",
    long_description = open('readme.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type = "text/markdown",
    author = "Soumil Maitra",
    author_email = "smaitra_be19@thapar.edu",
    url="https://github.com/maitra100/topsis/archive/refs/tags/0.0.1.tar.gz",
    keywords = ['Topsis', 'UCS654', '101903663'],
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['pandas', 'tabulate'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3' 
    ]
)
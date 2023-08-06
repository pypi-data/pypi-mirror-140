from setuptools import setup, find_packages

setup(
    name = "Topsis-yash-101903780",
    version = "0.0.2",
    license = "MIT",
    description = "A Python package to find TOPSIS for multi-criteria decision analysis method",
    long_description = open('readme.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type = "text/markdown",
    author = "Yash Kumar",
    author_email = "ykumar1_be19@thapar.edu",
    url = "https://github.com/YashKumar-0307/topsis/archive/refs/tags/0.0.2.tar.gz",
    keywords = ['topsis', 'UCS654', '101903780'],
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
from setuptools import setup, find_packages

setup(
    name = "Topsis-Shruti_101903372",
    version = "0.0.1",
    license = "MIT",
    description = "A Python package to find TOPSIS for multi-criteria decision analysis method",
    long_description = open('readme.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type = "text/markdown",
    author = "Shruti Katyal",
    author_email = "skatyal_be19@thapar.edu",
    keywords = ['topsis', 'UCS538', 'TIET'],
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
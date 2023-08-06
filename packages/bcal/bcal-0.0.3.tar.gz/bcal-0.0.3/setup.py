from setuptools import setup,find_packages


with open('README.txt') as f:
    README = f.read()

setup(
    author="Raviteja",
    author_email="tejarockz100@gmail.com",
    name='bcal',
    license="MIT",
    description='bcal is a python package for basic calculations.',
    version='v0.0.3',
    long_description=README,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=['requests'],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
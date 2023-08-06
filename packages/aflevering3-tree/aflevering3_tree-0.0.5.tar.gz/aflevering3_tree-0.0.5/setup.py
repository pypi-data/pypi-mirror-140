from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='aflevering3_tree',
    version='0.0.5',
    description='A collection of functions from Aflevering 3',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Christopher L. Kristiansen',
    author_email='Christopher@kristiansenz.com',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=['']
)
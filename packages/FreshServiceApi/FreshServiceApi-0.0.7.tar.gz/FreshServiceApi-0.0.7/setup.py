from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Information Technology',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='FreshServiceApi',
    version='0.0.7',
    description='Modules for the FreshService API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Stephen Fitzsimmons',
    license='MIT',
    classifiers=classifiers,
    keywords='FreshService',
    packages=find_packages(),
    install_requires=['requests']
)
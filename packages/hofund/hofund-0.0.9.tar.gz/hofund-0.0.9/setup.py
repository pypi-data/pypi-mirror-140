from setuptools import setup, find_packages
with open("Readme.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'hofund',
    version = '0.0.9',
    author = 'Ramey Girdhar',
    author_email = 'ramey.girdhar@gojek.com',
    license = 'UNLICENSED',
    description = 'allows user to search protos using stencil',
    long_description = long_description,
    include_package_data=True,
    long_description_content_type = "text/markdown",
    url = 'https://source.golabs.io/asgard/spikes/prototypes/hofund',
    py_modules = ['hofund'],
    packages = find_packages(),
    install_requires = [
        'aiohttp==3.8.1',
        'aiodns==3.0.0',
        'cchardet==2.1.7',
        'pandas==1.4.0',
        'setuptools==58.1.0',
        'requests==2.27.1',
        'protobuf==3.19.4',
    ],
    python_requires='>=3.9',
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        hofund=hofund:main
    '''
)
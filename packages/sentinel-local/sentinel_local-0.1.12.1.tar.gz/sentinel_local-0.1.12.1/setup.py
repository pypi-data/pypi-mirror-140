from setuptools import setup, find_packages
import pathlib

VERSION = '0.1.12.1'
DESCRIPTION = 'Local Processing of Data Based on CXL Created Algorithms'
HERE = pathlib.Path(__file__).parent
README = (HERE/"README.md").read_text()


setup(
    name="sentinel_local",
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown", 
    url="https://github.com/cxl-garage/sentinel-laptop",
    author="Sam Kelly",
    author_email="sam@conservationxlabs.org",
    py_modules = ['sentinel_local','src'],
    classifiers=[ 
        "License :: OSI Approved :: MIT License", 
        "Programming Language :: Python :: 3", 
        "Programming Language :: Python :: 3.7", 
   ], 
    packages=find_packages(),
    includepackagedata=True, 
    install_requires=["docker","GPUtil","numpy","pandas","Pillow","requests","tqdm","google-cloud-artifact-registry"], 
    entrypoints= {
        'console_scripts': [
            'sentinel_run=sentinel_local:run' 
            'sentinel_download=sentinel_local:download' 
        ]
    }
    
)
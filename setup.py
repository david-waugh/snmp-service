from setuptools import find_packages, setup

NAME = 'snmp-service'
DESCRIPTION = 'Developed as part of a proof-of-concept for a University dissertation piece. A limited RESTful API service for interacting with Juniper/Cisco devices using SNMP.'
AUTHOR = 'David Waugh'
EMAIL = 'david-waugh@hotmail.com'
REQUIRES_PYTHON = '>=3.10'
VERSION = '0.1.0'

REQUIRED_PACKAGES = (
    'pysnmp', 
    'pysnmp-mibs', 
    'pysmi', 
    'pydantic', 
    'fastapi'
)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
)

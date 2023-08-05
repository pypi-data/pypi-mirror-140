"""Setup Project."""
from setuptools import find_packages, setup

setup(
    name="komle-plus",
    version="0.3.0",
    description="A python library to help with WITSML v1.4.1.1 and v2.0",
    url="https://github.com/kle043/komle",
    packages=find_packages(exclude=("tests",)),
    author="kle043",
    author_email="pale.dorg@gmail.com",
    include_package_data=True,
    package_data={
        "komle": ["WMLS.WSDL", "witsmlUnitDict.xml"],
    },
    install_requires=[
        "suds-py3==1.4.5",
        "PyXB-X==1.2.6",
        "requests==2.27.1"
    ],
    tests_require=["pytest>=7.0.1"],
    python_requires=">=3.9",
)

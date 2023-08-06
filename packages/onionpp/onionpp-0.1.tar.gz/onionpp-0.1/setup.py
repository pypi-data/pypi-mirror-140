from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension


ext_modules = [
    Pybind11Extension("onionpp", ["python_binding.cpp"])
]


setup(
    long_description=open("README.md", "r").read(),
    name="onionpp",
    version="0.1",
    description="embed tor into your application",
    author="Pascal Eberlein",
    author_email="pascal@eberlein.io",
    url="https://github.com/nbdy/onionpp",
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords="tor embedded",
    packages=find_packages(),
    long_description_content_type="text/markdown",
    ext_modules=ext_modules,
    headers=['onionpp.h']
)
